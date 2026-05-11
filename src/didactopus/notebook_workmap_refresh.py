from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .notebook_promotion_pipeline import run_notebook_promotion_pipeline


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def run_notebook_workmap_refresh(
    work_map_path: str | Path,
    *,
    output_path: str | Path | None = None,
    phrase_inventory_output: str | Path | None = None,
    top_n: int = 50,
) -> dict[str, Any]:
    work_map_file = Path(work_map_path).resolve()
    work_root = work_map_file.parent.parent
    work_map = _load_json(work_map_file)

    binding_path = _resolve(work_root, str(work_map["primary_hub"]["binding_path"]))
    canonical_dir = _resolve(work_root, str(work_map["groundrecall_paths"]["canonical_export_dir"]))
    manifest_path = _resolve(work_root, str(work_map["groundrecall_paths"]["batch_manifest"]))

    report_path = (
        Path(output_path).resolve()
        if output_path
        else _resolve(work_root, str(work_map["groundrecall_paths"]["pipeline_report_json"]))
    )
    phrase_path = (
        Path(phrase_inventory_output).resolve()
        if phrase_inventory_output
        else _resolve(work_root, str(work_map["groundrecall_paths"]["pipeline_phrase_inventory_json"]))
    )

    normalized_roots = [
        _resolve(work_root, item)
        for item in (work_map.get("canonical_sources", {}) or {}).get("normalized_roots", [])
    ]

    seed_terms = [
        str(item.get("concept", "")).strip()
        for items in (work_map.get("promotion_priority", {}) or {}).values()
        for item in items or []
        if str(item.get("concept", "")).strip()
    ]

    if not seed_terms:
        manifest_data = _load_json(manifest_path) if manifest_path.suffix == ".json" else None
        if manifest_data:
            seed_terms = [
                str(item.get("concept", "")).strip()
                for items in (manifest_data.get("promotion_priority", {}) or {}).values()
                for item in items or []
                if str(item.get("concept", "")).strip()
            ]
        else:
            import yaml  # local import to avoid unnecessary dependency at module import time

            manifest_yaml = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            seed_terms = [
                str(item.get("concept", "")).strip()
                for items in (manifest_yaml.get("promotion_priority", {}) or {}).values()
                for item in items or []
                if str(item.get("concept", "")).strip()
            ]

    summary = run_notebook_promotion_pipeline(
        binding_path=binding_path,
        manifest_path=manifest_path,
        canonical_dir=canonical_dir,
        output_path=report_path,
        phrase_inventory_output=phrase_path,
        phrase_inputs=normalized_roots,
        seed_terms=seed_terms,
        top_n=top_n,
    )
    return {
        "work_map_path": str(work_map_file),
        "work_root": str(work_root),
        "report_path": summary["report_path"],
        "markdown_path": summary["markdown_path"],
        "report": summary["report"],
    }
