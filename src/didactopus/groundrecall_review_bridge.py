from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .review_export import export_review_state_json, export_review_ui_data
from .review_schema import ConceptReviewEntry, DraftPackData, ReviewSession


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def _claim_summary(claims: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for claim in claims[:3]:
        grounding = claim.get("grounding_status", "unknown")
        lines.append(f"Claim: {claim.get('claim_text', '')} [{grounding}]")
    if len(claims) > 3:
        lines.append(f"{len(claims) - 3} additional claims omitted from notes summary.")
    return lines


def build_review_session_from_import(import_dir: str | Path, reviewer: str = "GroundRecall Import") -> ReviewSession:
    base = Path(import_dir)
    manifest = _read_json(base / "manifest.json")
    lint_payload = _read_json(base / "lint_findings.json")
    claims = _read_jsonl(base / "claims.jsonl")
    concepts = _read_jsonl(base / "concepts.jsonl")

    claims_by_concept: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        for concept_id in claim.get("concept_ids", []):
            claims_by_concept[concept_id].append(claim)

    findings_by_target: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    concept_findings: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in lint_payload.get("findings", []):
        findings_by_target[finding["target_id"]].append(finding)
    for claim in claims:
        for concept_id in claim.get("concept_ids", []):
            concept_findings[concept_id].extend(findings_by_target.get(claim["claim_id"], []))
    for concept in concepts:
        concept_findings[concept["concept_id"]].extend(findings_by_target.get(concept["concept_id"], []))

    entries: list[ConceptReviewEntry] = []
    for concept in concepts:
        concept_id = concept["concept_id"]
        related_claims = claims_by_concept.get(concept_id, [])
        related_findings = concept_findings.get(concept_id, [])
        has_errors = any(item["severity"] == "error" for item in related_findings)
        all_grounded = bool(related_claims) and all(item.get("grounding_status") == "grounded" for item in related_claims)
        status = "needs_review"
        if not has_errors and all_grounded:
            status = "provisional"

        notes = _claim_summary(related_claims)
        notes.extend(item["message"] for item in related_findings[:5])

        entries.append(
            ConceptReviewEntry(
                concept_id=concept_id.replace("concept::", "", 1),
                title=concept.get("title", concept_id),
                description=concept.get("description", ""),
                prerequisites=[],
                mastery_signals=[],
                status=status,
                notes=notes,
            )
        )

    conflicts = [item["message"] for item in lint_payload.get("findings", []) if item["severity"] == "error"]
    review_flags = [item["message"] for item in lint_payload.get("findings", []) if item["severity"] == "warning"]
    pack = {
        "name": f"groundrecall-import-{manifest['import_id']}",
        "display_name": f"GroundRecall Import {manifest['import_id']}",
        "version": "0.1.0-draft",
        "source_import_id": manifest["import_id"],
        "source_root": manifest.get("source_root", ""),
    }
    attribution = {
        "source_repo_kind": manifest.get("source_repo_kind", "llmwiki"),
        "source_root": manifest.get("source_root", ""),
        "imported_at": manifest.get("imported_at", ""),
        "machine_id": manifest.get("machine_id", ""),
        "rights_note": "Imported llmwiki-style corpus requires review before promotion.",
    }
    return ReviewSession(
        reviewer=reviewer,
        draft_pack=DraftPackData(
            pack=pack,
            concepts=entries,
            conflicts=conflicts,
            review_flags=review_flags,
            attribution=attribution,
        ),
    )


def export_review_bundle_from_import(import_dir: str | Path, out_dir: str | Path | None = None, reviewer: str = "GroundRecall Import") -> dict[str, str]:
    base = Path(import_dir)
    target = Path(out_dir) if out_dir is not None else base
    target.mkdir(parents=True, exist_ok=True)
    session = build_review_session_from_import(base, reviewer=reviewer)
    review_state_path = target / "review_session.json"
    export_review_state_json(session, review_state_path)
    export_review_ui_data(session, target)
    return {
        "review_session_json": str(review_state_path),
        "review_data_json": str(target / "review_data.json"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Didactopus review artifacts from a GroundRecall import.")
    parser.add_argument("import_dir")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--reviewer", default="GroundRecall Import")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = export_review_bundle_from_import(args.import_dir, out_dir=args.out_dir, reviewer=args.reviewer)
    print(json.dumps(outputs, indent=2))
