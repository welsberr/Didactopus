from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .pack_to_frontend import convert_pack


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def notebook_summary(pack_dir: str | Path) -> dict[str, Any]:
    payload = convert_pack(pack_dir)
    return payload.get("notebook", {}) or {}


def compare_notebook_packs(
    baseline_pack_dir: str | Path,
    augmented_pack_dir: str | Path,
) -> dict[str, Any]:
    baseline_pack_dir = Path(baseline_pack_dir)
    augmented_pack_dir = Path(augmented_pack_dir)

    baseline_frontend = convert_pack(baseline_pack_dir)
    augmented_frontend = convert_pack(augmented_pack_dir)
    baseline_notebook = baseline_frontend.get("notebook", {}) or {}
    augmented_notebook = augmented_frontend.get("notebook", {}) or {}

    baseline_bundle = _load_json(baseline_pack_dir / "groundrecall_query_bundle.json")
    augmented_bundle = _load_json(augmented_pack_dir / "groundrecall_query_bundle.json")
    augmented_page = _load_json(augmented_pack_dir / "notebook_page.json")

    return {
        "baseline_notebook": baseline_notebook,
        "augmented_notebook": augmented_notebook,
        "delta": {
            "claimCount": int(augmented_notebook.get("claimCount", 0)) - int(baseline_notebook.get("claimCount", 0)),
            "distinctionCount": int(augmented_notebook.get("distinctionCount", 0)) - int(baseline_notebook.get("distinctionCount", 0)),
            "supportingObservationCount": int(augmented_notebook.get("supportingObservationCount", 0)) - int(baseline_notebook.get("supportingObservationCount", 0)),
            "relatedConceptCount": int(augmented_notebook.get("relatedConceptCount", 0)) - int(baseline_notebook.get("relatedConceptCount", 0)),
            "sourceRoleKeys": sorted(
                set((augmented_notebook.get("sourceRoleSummary", {}) or {}).keys())
                - set((baseline_notebook.get("sourceRoleSummary", {}) or {}).keys())
            ),
        },
        "bundle_excerpt": {
            "claim_ids": [item.get("claim_id") for item in augmented_bundle.get("relevant_claims", [])],
            "source_role_summary": augmented_bundle.get("source_role_summary", {}),
            "key_distinctions": (augmented_bundle.get("key_distinctions", []) or [])[:8],
        },
        "page_summary": augmented_page.get("summary", {}),
    }


def comparison_markdown(title: str, comparison: dict[str, Any]) -> str:
    baseline = comparison.get("baseline_notebook", {}) or {}
    augmented = comparison.get("augmented_notebook", {}) or {}
    delta = comparison.get("delta", {}) or {}
    lines = [
        f"# {title}",
        "",
        "## Baseline",
        f"- claimCount: {baseline.get('claimCount', 0)}",
        f"- sourceRoleSummary: {baseline.get('sourceRoleSummary', {})}",
        f"- distinctionCount: {baseline.get('distinctionCount', 0)}",
        f"- supportingObservationCount: {baseline.get('supportingObservationCount', 0)}",
        "",
        "## Augmented",
        f"- claimCount: {augmented.get('claimCount', 0)}",
        f"- sourceRoleSummary: {augmented.get('sourceRoleSummary', {})}",
        f"- distinctionCount: {augmented.get('distinctionCount', 0)}",
        f"- supportingObservationCount: {augmented.get('supportingObservationCount', 0)}",
        "",
        "## Delta",
        f"- claimCount: {delta.get('claimCount', 0):+d}",
        f"- distinctionCount: {delta.get('distinctionCount', 0):+d}",
        f"- supportingObservationCount: {delta.get('supportingObservationCount', 0):+d}",
        f"- relatedConceptCount: {delta.get('relatedConceptCount', 0):+d}",
        f"- new source role keys: {delta.get('sourceRoleKeys', [])}",
    ]
    return "\n".join(lines) + "\n"


def write_notebook_comparison_report(
    baseline_pack_dir: str | Path,
    augmented_pack_dir: str | Path,
    outdir: str | Path,
    title: str = "Notebook Augmentation Comparison",
) -> dict[str, Any]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    comparison = compare_notebook_packs(baseline_pack_dir, augmented_pack_dir)
    (outdir / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    (outdir / "comparison.md").write_text(comparison_markdown(title, comparison), encoding="utf-8")
    (outdir / "frontend_pack_with_notebook.json").write_text(
        json.dumps(convert_pack(augmented_pack_dir), indent=2),
        encoding="utf-8",
    )
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare baseline and augmented Notebook pack outputs.")
    parser.add_argument("baseline_pack_dir")
    parser.add_argument("augmented_pack_dir")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--title", default="Notebook Augmentation Comparison")
    args = parser.parse_args()
    comparison = write_notebook_comparison_report(
        args.baseline_pack_dir,
        args.augmented_pack_dir,
        args.outdir,
        title=args.title,
    )
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
