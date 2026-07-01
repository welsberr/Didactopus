from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .archive_phrase_inventory import write_archive_phrase_inventory_report
from .first_ring_batch_promotion import run_first_ring_batch_promotion
from .hub_bundle_rebuild import rebuild_hub_bundle_from_binding


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hub_metrics(binding_path: str | Path) -> dict[str, Any]:
    binding_file = Path(binding_path)
    binding = _load_json(binding_file)
    hub_path = (binding_file.parent / binding["primary_artifacts"]["groundrecall_query_bundle"]).resolve()
    page_path = (binding_file.parent / binding["primary_artifacts"]["notebook_page"]).resolve()
    hub = _load_json(hub_path) if hub_path.exists() else {}
    page = _load_json(page_path) if page_path.exists() else {}
    return {
        "hub_bundle_path": str(hub_path),
        "notebook_page_path": str(page_path),
        "hub": {
            "claim_count": len(hub.get("relevant_claims", []) or []),
            "supporting_observation_count": len(hub.get("supporting_observations", []) or []),
            "related_concept_count": len(hub.get("related_concepts", []) or []),
            "source_artifact_count": len(hub.get("source_artifacts", []) or []),
            "source_role_summary": hub.get("source_role_summary", {}) or {},
            "distinction_count": len(hub.get("key_distinctions", []) or []),
        },
        "page_summary": page.get("summary", {}) or {},
    }


def _delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in (
        "claim_count",
        "supporting_observation_count",
        "related_concept_count",
        "source_artifact_count",
        "distinction_count",
    ):
        out[key] = (after.get(key) or 0) - (before.get(key) or 0)
    return out


def run_notebook_promotion_pipeline(
    *,
    binding_path: str | Path,
    manifest_path: str | Path,
    canonical_dir: str | Path,
    output_path: str | Path,
    phrase_inventory_output: str | Path | None = None,
    phrase_inputs: list[str | Path] | None = None,
    seed_terms: list[str] | None = None,
    top_n: int = 50,
) -> dict[str, Any]:
    before = _hub_metrics(binding_path)

    phrase_summary: dict[str, Any] | None = None
    if phrase_inventory_output and phrase_inputs:
        phrase_summary = write_archive_phrase_inventory_report(
            phrase_inputs,
            phrase_inventory_output,
            seed_terms=seed_terms or [],
            top_n=top_n,
        )

    batch_summary = run_first_ring_batch_promotion(manifest_path, canonical_dir)
    rebuild_summary = rebuild_hub_bundle_from_binding(binding_path)
    after = _hub_metrics(binding_path)

    generated = batch_summary.get("generated", []) or []
    weak_nodes = [item for item in generated if (item.get("claim_count") or 0) < 2]
    strong_nodes = [item for item in generated if (item.get("claim_count") or 0) >= 2]

    report = {
        "binding_path": str(Path(binding_path)),
        "manifest_path": str(Path(manifest_path)),
        "canonical_dir": str(Path(canonical_dir)),
        "phrase_inventory": phrase_summary,
        "batch_promotion": {
            "report_path": batch_summary.get("report_path"),
            "generated_count": batch_summary.get("generated_count", len(generated)),
            "strong_node_count": len(strong_nodes),
            "weak_node_count": len(weak_nodes),
            "weak_nodes": [
                {
                    "concept": item.get("concept"),
                    "claim_count": item.get("claim_count"),
                    "status": item.get("status"),
                }
                for item in weak_nodes
            ],
        },
        "hub_rebuild": rebuild_summary,
        "before": before,
        "after": after,
        "delta": {
            "hub": _delta(before.get("hub", {}) or {}, after.get("hub", {}) or {}),
        },
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path = out.with_suffix(".md")
    lines = [
        "# Notebook Promotion Pipeline",
        "",
        f"- binding: `{report['binding_path']}`",
        f"- manifest: `{report['manifest_path']}`",
        f"- batch generated: `{report['batch_promotion']['generated_count']}`",
        f"- strong nodes: `{report['batch_promotion']['strong_node_count']}`",
        f"- weak nodes: `{report['batch_promotion']['weak_node_count']}`",
        "",
        "## Hub Delta",
    ]
    for key, value in report["delta"]["hub"].items():
        lines.append(f"- `{key}`: `{value:+d}`")
    if report["batch_promotion"]["weak_nodes"]:
        lines.extend(["", "## Weak Nodes"])
        for item in report["batch_promotion"]["weak_nodes"]:
            lines.append(
                f"- `{item['concept']}` claims=`{item['claim_count']}` status=`{item['status']}`"
            )
    if phrase_summary:
        lines.extend(
            [
                "",
                "## Phrase Inventory",
                f"- report: `{phrase_summary['report_path']}`",
                f"- documents: `{phrase_summary['summary']['document_count']}`",
                f"- prioritized concepts: `{phrase_summary['summary']['distinct_phrase_count']}`",
            ]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report_path": str(out), "markdown_path": str(md_path), "report": report}
