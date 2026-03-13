from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml
import networkx as nx

from . import __version__ as DIDACTOPUS_VERSION
from .artifact_schemas import (
    ConceptsFile,
    PackManifest,
    ProjectsFile,
    RoadmapFile,
    RubricsFile,
    validate_top_level_key,
)

REQUIRED_FILES = ["pack.yaml", "concepts.yaml", "roadmap.yaml", "projects.yaml", "rubrics.yaml"]


def _parse_version(version: str) -> tuple[int, ...]:
    parts = []
    for chunk in version.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _version_in_range(version: str, min_version: str, max_version: str) -> bool:
    v = _parse_version(version)
    vmin = _parse_version(min_version)
    vmax = _parse_version(max_version)
    return vmin <= v <= vmax


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


def _check_duplicate_ids(entries: list[Any], label: str) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry.id in seen:
            errors.append(f"duplicate {label} id: {entry.id}")
        seen.add(entry.id)
    return errors


def _check_concept_references(concepts_file: ConceptsFile, roadmap_file: RoadmapFile, projects_file: ProjectsFile) -> list[str]:
    errors: list[str] = []
    concept_ids = {c.id for c in concepts_file.concepts}
    for concept in concepts_file.concepts:
        for prereq in concept.prerequisites:
            if prereq not in concept_ids:
                errors.append(f"unknown concept prerequisite '{prereq}' referenced by concept '{concept.id}'")
    for stage in roadmap_file.stages:
        for concept_id in stage.concepts:
            if concept_id not in concept_ids:
                errors.append(f"unknown concept '{concept_id}' referenced by roadmap stage '{stage.id}'")
    for project in projects_file.projects:
        for prereq in project.prerequisites:
            if prereq not in concept_ids:
                errors.append(f"unknown concept prerequisite '{prereq}' referenced by project '{project.id}'")
    return errors


def _check_core_compatibility(manifest: PackManifest) -> list[str]:
    if _version_in_range(DIDACTOPUS_VERSION, manifest.didactopus_min_version, manifest.didactopus_max_version):
        return []
    return [f"incompatible with Didactopus core version {DIDACTOPUS_VERSION}; supported range is {manifest.didactopus_min_version}..{manifest.didactopus_max_version}"]


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
        result.errors.extend(_check_core_compatibility(result.manifest))

        concepts_data = _load_yaml(pack_path / "concepts.yaml")
        result.errors.extend(validate_top_level_key(concepts_data, "concepts"))
        concepts_file = None
        if "concepts" in concepts_data:
            concepts_file = ConceptsFile.model_validate(concepts_data)
            result.loaded_files["concepts"] = concepts_file
            result.errors.extend(_check_duplicate_ids(concepts_file.concepts, "concept"))

        roadmap_data = _load_yaml(pack_path / "roadmap.yaml")
        result.errors.extend(validate_top_level_key(roadmap_data, "stages"))
        roadmap_file = None
        if "stages" in roadmap_data:
            roadmap_file = RoadmapFile.model_validate(roadmap_data)
            result.loaded_files["roadmap"] = roadmap_file
            result.errors.extend(_check_duplicate_ids(roadmap_file.stages, "roadmap stage"))

        projects_data = _load_yaml(pack_path / "projects.yaml")
        result.errors.extend(validate_top_level_key(projects_data, "projects"))
        projects_file = None
        if "projects" in projects_data:
            projects_file = ProjectsFile.model_validate(projects_data)
            result.loaded_files["projects"] = projects_file
            result.errors.extend(_check_duplicate_ids(projects_file.projects, "project"))

        rubrics_data = _load_yaml(pack_path / "rubrics.yaml")
        result.errors.extend(validate_top_level_key(rubrics_data, "rubrics"))
        if "rubrics" in rubrics_data:
            rubrics_file = RubricsFile.model_validate(rubrics_data)
            result.loaded_files["rubrics"] = rubrics_file
            result.errors.extend(_check_duplicate_ids(rubrics_file.rubrics, "rubric"))

        if concepts_file and roadmap_file and projects_file:
            result.errors.extend(_check_concept_references(concepts_file, roadmap_file, projects_file))
    except Exception as exc:
        result.errors.append(str(exc))

    result.is_valid = not result.errors
    return result


def discover_domain_packs(base_dirs: list[str | Path]) -> list[PackValidationResult]:
    results: list[PackValidationResult] = []
    for base_dir in base_dirs:
        base = Path(base_dir)
        if not base.exists():
            continue
        for pack_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            results.append(validate_pack(pack_dir))
    return results


def check_pack_dependencies(results: list[PackValidationResult]) -> list[str]:
    errors: list[str] = []
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
                errors.append(f"pack '{result.manifest.name}' requires '{dep.name}' version {dep.min_version}..{dep.max_version}, but found {dep_manifest.version}")
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
