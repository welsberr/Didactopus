from __future__ import annotations

from pathlib import Path
import sys

import yaml

from .doclift_bundle_demo import run_doclift_bundle_demo


def run_doclift_bundle_with_groundrecall(
    *,
    groundrecall_store_dir: str | Path,
    groundrecall_concept_ref: str,
    bundle_dir: str | Path,
    course_title: str,
    pack_dir: str | Path,
    author: str = "doclift bundle import",
    license_name: str = "See source bundle metadata",
) -> dict:
    export_groundrecall_query_bundle = _load_groundrecall_export()
    pack_dir = Path(pack_dir)
    export_dir = pack_dir / "_groundrecall"
    exported = export_groundrecall_query_bundle(
        groundrecall_store_dir,
        groundrecall_concept_ref,
        export_dir,
    )
    summary = run_doclift_bundle_demo(
        bundle_dir=bundle_dir,
        course_title=course_title,
        pack_dir=pack_dir,
        author=author,
        license_name=license_name,
        groundrecall_query_bundle_path=exported["bundle_path"],
    )
    summary["groundrecall_concept_ref"] = groundrecall_concept_ref
    summary["groundrecall_query_bundle_path"] = exported["bundle_path"]
    sidecar_path = exported.get("bayesian_reliability_markdown_path", "")
    if sidecar_path:
        copied = _copy_bayesian_reliability_sidecar(Path(sidecar_path), pack_dir)
        if copied:
            summary["bayesian_reliability_markdown_path"] = str(copied)
    return summary


def _copy_bayesian_reliability_sidecar(source_path: Path, pack_dir: Path) -> Path | None:
    if not source_path.exists():
        return None
    destination = pack_dir / "bayesian_reliability.md"
    destination.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
    pack_yaml_path = pack_dir / "pack.yaml"
    if pack_yaml_path.exists():
        pack = yaml.safe_load(pack_yaml_path.read_text(encoding="utf-8")) or {}
        artifacts = list(pack.get("supporting_artifacts", []) or [])
        if "bayesian_reliability.md" not in artifacts:
            artifacts.append("bayesian_reliability.md")
        pack["supporting_artifacts"] = artifacts
        pack_yaml_path.write_text(yaml.safe_dump(pack, sort_keys=False), encoding="utf-8")
    return destination


def _load_groundrecall_export():
    groundrecall_src = Path("/home/netuser/bin/GroundRecall/src")
    if groundrecall_src.exists():
        sys.path.insert(0, str(groundrecall_src))
    from groundrecall.export import export_groundrecall_query_bundle  # type: ignore

    return export_groundrecall_query_bundle
