from __future__ import annotations

"""Legacy flat GroundRecall lint module.

Compatibility path retained during the internal namespace migration.
Prefer imports and CLI usage under ``didactopus.groundrecall.lint`` or
``didactopus.groundrecall.cli`` for new code.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def lint_import_directory(import_dir: str | Path) -> dict[str, Any]:
    base = Path(import_dir)
    manifest = _read_json(base / "manifest.json")
    artifacts = _read_jsonl(base / "artifacts.jsonl")
    observations = _read_jsonl(base / "observations.jsonl")
    claims = _read_jsonl(base / "claims.jsonl")
    concepts = _read_jsonl(base / "concepts.jsonl")
    relations = _read_jsonl(base / "relations.jsonl")

    findings: list[dict[str, Any]] = []
    observation_by_id = {row["observation_id"]: row for row in observations}
    concept_ids = {row["concept_id"] for row in concepts}

    text_counter = Counter(row["claim_text"].strip().lower() for row in claims if row.get("claim_text", "").strip())
    claim_ids = {row["claim_id"] for row in claims}
    for claim in claims:
        claim_text = claim.get("claim_text", "").strip()
        if not claim.get("source_observation_ids"):
            findings.append(
                {
                    "severity": "error",
                    "code": "claim_missing_observation",
                    "target_id": claim["claim_id"],
                    "message": "Claim has no source observation ids.",
                }
            )
        if not claim.get("concept_ids"):
            findings.append(
                {
                    "severity": "warning",
                    "code": "claim_missing_concept",
                    "target_id": claim["claim_id"],
                    "message": "Claim is not associated with any concepts.",
                }
            )
        if claim.get("grounding_status") == "ungrounded":
            findings.append(
                {
                    "severity": "warning",
                    "code": "claim_ungrounded",
                    "target_id": claim["claim_id"],
                    "message": "Claim is ungrounded and should not be promoted directly.",
                }
            )
        if claim_text and text_counter[claim_text.lower()] > 1:
            findings.append(
                {
                    "severity": "warning",
                    "code": "duplicate_claim_text",
                    "target_id": claim["claim_id"],
                    "message": "Claim text duplicates another imported claim.",
                }
            )
        for obs_id in claim.get("source_observation_ids", []):
            if obs_id not in observation_by_id:
                findings.append(
                    {
                        "severity": "error",
                        "code": "claim_observation_missing",
                        "target_id": claim["claim_id"],
                        "message": f"Claim references missing observation {obs_id}.",
                    }
                )
        for target_claim_id in claim.get("contradicts_claim_ids", []):
            if target_claim_id not in claim_ids:
                findings.append(
                    {
                        "severity": "warning",
                        "code": "unresolved_contradiction_ref",
                        "target_id": claim["claim_id"],
                        "message": f"Claim references missing contradiction target {target_claim_id}.",
                    }
                )
        for target_claim_id in claim.get("supersedes_claim_ids", []):
            if target_claim_id not in claim_ids:
                findings.append(
                    {
                        "severity": "warning",
                        "code": "unresolved_supersession_ref",
                        "target_id": claim["claim_id"],
                        "message": f"Claim references missing supersession target {target_claim_id}.",
                    }
                )
        if claim.get("contradicts_claim_ids") and claim.get("supersedes_claim_ids"):
            findings.append(
                {
                    "severity": "warning",
                    "code": "claim_mixed_conflict_and_supersession",
                    "target_id": claim["claim_id"],
                    "message": "Claim marks both contradiction and supersession targets; review the intended relation.",
                }
            )

    concept_sources: defaultdict[str, set[str]] = defaultdict(set)
    for claim in claims:
        for concept_id in claim.get("concept_ids", []):
            concept_sources[concept_id].add(claim["claim_id"])
    for relation in relations:
        concept_sources[relation.get("source_id", "")].add(relation["relation_id"])
        concept_sources[relation.get("target_id", "")].add(relation["relation_id"])

    for concept in concepts:
        if not concept_sources.get(concept["concept_id"]):
            findings.append(
                {
                    "severity": "warning",
                    "code": "orphan_concept",
                    "target_id": concept["concept_id"],
                    "message": "Concept has no connected claims or relations.",
                }
            )

    for relation in relations:
        if relation.get("source_id") not in concept_ids:
            findings.append(
                {
                    "severity": "error",
                    "code": "relation_missing_source",
                    "target_id": relation["relation_id"],
                    "message": f"Relation source {relation.get('source_id')} is missing.",
                }
            )
        if relation.get("target_id") not in concept_ids:
            findings.append(
                {
                    "severity": "error",
                    "code": "relation_missing_target",
                    "target_id": relation["relation_id"],
                    "message": f"Relation target {relation.get('target_id')} is missing.",
                }
            )

    for observation in observations:
        role = observation.get("role")
        if role == "summary" and observation.get("grounding_status") == "ungrounded":
            findings.append(
                {
                    "severity": "warning",
                    "code": "ungrounded_summary",
                    "target_id": observation["observation_id"],
                    "message": "Summary observation is ungrounded.",
                }
            )

    summary = {
        "artifact_count": len(artifacts),
        "observation_count": len(observations),
        "claim_count": len(claims),
        "concept_count": len(concepts),
        "relation_count": len(relations),
        "error_count": sum(1 for item in findings if item["severity"] == "error"),
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
    }
    return {
        "import_id": manifest["import_id"],
        "import_mode": manifest["import_mode"],
        "summary": summary,
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lint GroundRecall import artifacts.")
    parser.add_argument("import_dir")
    parser.add_argument("--out", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = lint_import_directory(args.import_dir)
    out_path = Path(args.out) if args.out else Path(args.import_dir) / "lint_findings.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
