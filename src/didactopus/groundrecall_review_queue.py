from __future__ import annotations

import argparse
import json
from collections import defaultdict
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


def _triage_lane(item: dict[str, Any], finding_codes: set[str]) -> str:
    if {"claim_ungrounded", "ungrounded_summary"} & finding_codes:
        return "source_cleanup"
    if {"relation_missing_source", "relation_missing_target", "orphan_concept"} & finding_codes:
        return "conflict_resolution"
    return "knowledge_capture"


def _priority(item: dict[str, Any], finding_codes: set[str]) -> int:
    priority = 50
    if item.get("grounding_status") == "grounded":
        priority -= 10
    if item.get("current_status") == "triaged":
        priority -= 5
    if any(code.startswith("claim_") or code.startswith("relation_") for code in finding_codes):
        priority += 20
    priority -= min(len(finding_codes) * 2, 10)
    return max(priority, 1)


def build_review_queue(import_dir: str | Path) -> dict[str, Any]:
    base = Path(import_dir)
    manifest = _read_json(base / "manifest.json")
    lint_payload = _read_json(base / "lint_findings.json")
    claims = _read_jsonl(base / "claims.jsonl")
    concepts = _read_jsonl(base / "concepts.jsonl")

    findings_by_target: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in lint_payload.get("findings", []):
        findings_by_target[finding["target_id"]].append(finding)

    queue: list[dict[str, Any]] = []

    for claim in claims:
        related = findings_by_target.get(claim["claim_id"], [])
        finding_codes = {item["code"] for item in related}
        queue.append(
            {
                "queue_id": f"rq_{claim['claim_id']}",
                "candidate_type": "claim",
                "candidate_id": claim["claim_id"],
                "title": claim["claim_text"][:100],
                "triage_lane": _triage_lane(claim, finding_codes),
                "priority": _priority(claim, finding_codes),
                "grounding_status": claim.get("grounding_status"),
                "status": "needs_review",
                "finding_codes": sorted(finding_codes),
                "concept_ids": list(claim.get("concept_ids", [])),
            }
        )

    for concept in concepts:
        related = findings_by_target.get(concept["concept_id"], [])
        finding_codes = {item["code"] for item in related}
        if not finding_codes:
            continue
        queue.append(
            {
                "queue_id": f"rq_{concept['concept_id'].replace('::', '_')}",
                "candidate_type": "concept",
                "candidate_id": concept["concept_id"],
                "title": concept["title"],
                "triage_lane": _triage_lane(concept, finding_codes),
                "priority": _priority(concept, finding_codes),
                "grounding_status": concept.get("grounding_status", "triaged"),
                "status": "needs_review",
                "finding_codes": sorted(finding_codes),
                "concept_ids": [concept["concept_id"]],
            }
        )

    queue.sort(key=lambda item: (item["priority"], item["candidate_type"], item["candidate_id"]))
    return {
        "import_id": manifest["import_id"],
        "queue_length": len(queue),
        "items": queue,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a GroundRecall review queue from import artifacts.")
    parser.add_argument("import_dir")
    parser.add_argument("--out", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = build_review_queue(args.import_dir)
    out_path = Path(args.out) if args.out else Path(args.import_dir) / "review_queue.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
