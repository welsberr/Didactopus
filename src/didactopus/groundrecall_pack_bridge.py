from __future__ import annotations

import os
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
    bayesian_label = exported.get("bayesian_reliability_label") or exported.get("bundle", {}).get("assessment_summary", {}).get("bayesian_label", "")
    if bayesian_label:
        summary["bayesian_reliability_label"] = bayesian_label
    sidecar_path = exported.get("bayesian_reliability_markdown_path", "")
    if sidecar_path:
        copied = _copy_supporting_artifact(Path(sidecar_path), pack_dir, "bayesian_reliability.md")
        if copied:
            summary["bayesian_reliability_markdown_path"] = str(copied)
    assessment_json_path = exported.get("bayesian_assessment_json_path", "")
    if assessment_json_path:
        copied = _copy_supporting_artifact(Path(assessment_json_path), pack_dir, "bayesian_assessment.json")
        if copied:
            summary["bayesian_assessment_json_path"] = str(copied)
    assessment_markdown_path = exported.get("bayesian_assessment_markdown_path", "")
    if assessment_markdown_path:
        copied = _copy_supporting_artifact(Path(assessment_markdown_path), pack_dir, "bayesian_assessment.md")
        if copied:
            summary["bayesian_assessment_markdown_path"] = str(copied)
    return summary


def _copy_supporting_artifact(source_path: Path, pack_dir: Path, filename: str) -> Path | None:
    if not source_path.exists():
        return None
    destination = pack_dir / filename
    destination.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
    pack_yaml_path = pack_dir / "pack.yaml"
    if pack_yaml_path.exists():
        pack = yaml.safe_load(pack_yaml_path.read_text(encoding="utf-8")) or {}
        artifacts = list(pack.get("supporting_artifacts", []) or [])
        if filename not in artifacts:
            artifacts.append(filename)
        pack["supporting_artifacts"] = artifacts
        pack_yaml_path.write_text(yaml.safe_dump(pack, sort_keys=False), encoding="utf-8")
    return destination


def _load_groundrecall_export():
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        Path(os.environ["GROUNDRECALL_SRC"]) if os.environ.get("GROUNDRECALL_SRC") else None,
        repo_root.parent / "GroundRecall" / "src",
    ]
    for groundrecall_src in candidates:
        if groundrecall_src is not None and (groundrecall_src / "groundrecall" / "export.py").exists():
            sys.path.insert(0, str(groundrecall_src))
            break
    from groundrecall.export import export_groundrecall_query_bundle  # type: ignore

    return export_groundrecall_query_bundle
