from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml
import networkx as nx

from . import __version__ as DIDACTOPUS_VERSION
from .artifact_schemas import ConceptsFile, PackManifest, ProjectsFile, RoadmapFile, RubricsFile

REQUIRED_FILES = ["pack.yaml", "concepts.yaml", "roadmap.yaml", "projects.yaml", "rubrics.yaml"]


def _parse_version(version: str) -> tuple[int, ...]:
    return tuple(int("".join(ch for ch in chunk if ch.isdigit()) or 0) for chunk in version.split("."))


def _version_in_range(version: str, min_version: str, max_version: str) -> bool:
    return _parse_version(min_version) <= _parse_version(version) <= _parse_version(max_version)


@dataclass
class PackValidationResult:
    pack_dir: Path
    manifest: PackManifest | None = None
    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    loaded_files: dict[str, Any] = field(default_factory=dict)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at top level")
    return data


def validate_pack(pack_dir: str | Path) -> PackValidationResult:
    pack_path = Path(pack_dir)
    result = PackValidationResult(pack_dir=pack_path)
    for filename in REQUIRED_FILES:
        if not (pack_path / filename).exists():
            result.errors.append(f"missing required file: {filename}")
    if result.errors:
        return result
    try:
        result.manifest = PackManifest.model_validate(_load_yaml(pack_path / "pack.yaml"))
        if not _version_in_range(DIDACTOPUS_VERSION, result.manifest.didactopus_min_version, result.manifest.didactopus_max_version):
            result.errors.append(
                f"incompatible with Didactopus core version {DIDACTOPUS_VERSION}; supported range is "
                f"{result.manifest.didactopus_min_version}..{result.manifest.didactopus_max_version}"
            )
        result.loaded_files["concepts"] = ConceptsFile.model_validate(_load_yaml(pack_path / "concepts.yaml"))
        result.loaded_files["roadmap"] = RoadmapFile.model_validate(_load_yaml(pack_path / "roadmap.yaml"))
        result.loaded_files["projects"] = ProjectsFile.model_validate(_load_yaml(pack_path / "projects.yaml"))
        result.loaded_files["rubrics"] = RubricsFile.model_validate(_load_yaml(pack_path / "rubrics.yaml"))
    except Exception as exc:
        result.errors.append(str(exc))
    result.is_valid = not result.errors
    return result


def discover_domain_packs(base_dirs: list[str | Path]) -> list[PackValidationResult]:
    results = []
    for base_dir in base_dirs:
        base = Path(base_dir)
        if not base.exists():
            continue
        for pack_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            results.append(validate_pack(pack_dir))
    return results


def check_pack_dependencies(results: list[PackValidationResult]) -> list[str]:
    errors = []
    manifest_by_name = {r.manifest.name: r.manifest for r in results if r.manifest is not None}
    for result in results:
        if result.manifest is None:
            continue
        for dep in result.manifest.dependencies:
            dep_manifest = manifest_by_name.get(dep.name)
            if dep_manifest is None:
                errors.append(f"pack '{result.manifest.name}' depends on missing pack '{dep.name}'")
                continue
            if not _version_in_range(dep_manifest.version, dep.min_version, dep.max_version):
                errors.append(
                    f"pack '{result.manifest.name}' requires '{dep.name}' version "
                    f"{dep.min_version}..{dep.max_version}, but found {dep_manifest.version}"
                )
    return errors


def build_dependency_graph(results: list[PackValidationResult]) -> nx.DiGraph:
    graph = nx.DiGraph()
    valid = [r for r in results if r.manifest is not None and r.is_valid]
    for result in valid:
        graph.add_node(result.manifest.name)
    for result in valid:
        for dep in result.manifest.dependencies:
            if dep.name in graph:
                graph.add_edge(dep.name, result.manifest.name)
    return graph


def detect_dependency_cycles(results: list[PackValidationResult]) -> list[list[str]]:
    return [cycle for cycle in nx.simple_cycles(build_dependency_graph(results))]


def topological_pack_order(results: list[PackValidationResult]) -> list[str]:
    return list(nx.topological_sort(build_dependency_graph(results)))
