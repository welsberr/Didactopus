from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_manifest(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _tier_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for tier_name, items in (manifest.get("promotion_priority") or {}).items():
        for item in items or []:
            copied = dict(item)
            copied["_tier"] = tier_name
            entries.append(copied)
    return entries


def _load_bundle_index(canonical_dir: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in sorted(canonical_dir.glob("query_bundle__*.json")):
        payload = _load_json(path)
        concept = payload.get("concept", {}) or {}
        candidates = {
            path.name,
            path.stem,
            str(concept.get("concept_id", "")).strip(),
            str(concept.get("concept_id", "")).replace("concept::", "", 1).strip(),
            _slugify(str(concept.get("title", ""))),
        }
        for key in candidates:
            if key:
                index[key] = {"path": path, "payload": payload}
    return index


def _find_existing_bundle(index: dict[str, dict[str, Any]], concept_slug: str) -> dict[str, Any] | None:
    candidates = [
        f"query_bundle__{concept_slug}.json",
        f"query_bundle__{concept_slug}",
        f"concept::{concept_slug}",
        concept_slug,
    ]
    for key in candidates:
        found = index.get(key)
        if found:
            return found
    return None


def _claim_matches(claim: dict[str, Any], keyword_phrases: list[str]) -> bool:
    text = str(claim.get("claim_text", "")).lower()
    return any(phrase in text for phrase in keyword_phrases)


def _build_synthetic_bundle(
    entry: dict[str, Any],
    canonical_dir: Path,
    bundle_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    concept_slug = str(entry["concept"]).strip()
    label = str(entry.get("label", concept_slug.replace("-", " ").title()))
    compose = entry.get("compose_from", {}) or {}
    keyword_phrases = [str(item).strip().lower() for item in compose.get("keyword_phrases", []) if str(item).strip()]
    bundle_refs = [str(item).strip() for item in compose.get("bundle_refs", []) if str(item).strip()]
    source_bundles = []
    for ref in bundle_refs:
        found = bundle_index.get(ref) or bundle_index.get(ref.removesuffix(".json"))
        if found:
            source_bundles.append(found)

    selected_claims: list[dict[str, Any]] = []
    seen_texts: set[str] = set()
    selected_obs_ids: set[str] = set()
    selected_related: dict[str, dict[str, Any]] = {}
    selected_artifacts: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []

    for bundle in source_bundles:
        payload = bundle["payload"]
        source_concept = payload.get("concept", {}) or {}
        source_concept_id = str(source_concept.get("concept_id", "")).strip()
        source_concept_title = str(source_concept.get("title", "")).strip()
        matched_count = 0
        for claim in payload.get("relevant_claims", []) or []:
            if not _claim_matches(claim, keyword_phrases):
                continue
            claim_text = str(claim.get("claim_text", "")).strip()
            if not claim_text or claim_text.lower() in seen_texts:
                continue
            seen_texts.add(claim_text.lower())
            matched_count += 1
            claim_copy = dict(claim)
            claim_copy["claim_id"] = f"synth_{concept_slug}_{len(selected_claims) + 1}"
            claim_copy["concept_ids"] = [f"concept::{concept_slug}"]
            metadata = dict(claim_copy.get("metadata", {}) or {})
            metadata.setdefault("source_lane", "batch_promotion")
            metadata.setdefault("source_bundle_concept", source_concept_title)
            claim_copy["metadata"] = metadata
            selected_claims.append(claim_copy)
            selected_obs_ids.update(str(item) for item in (claim.get("source_observation_ids", []) or []))
        if matched_count:
            if source_concept_id and source_concept_id != f"concept::{concept_slug}":
                selected_related[source_concept_id] = {
                    "concept_id": source_concept_id,
                    "title": source_concept_title,
                    "aliases": source_concept.get("aliases", []) or [],
                    "description": source_concept.get("description", ""),
                    "source_artifact_ids": source_concept.get("source_artifact_ids", []) or [],
                    "current_status": source_concept.get("current_status", "reviewed"),
                }
                relations.append(
                    {
                        "relation_id": f"rel_synth_{concept_slug}_{_slugify(source_concept_id)}",
                        "source_id": source_concept_id,
                        "target_id": f"concept::{concept_slug}",
                        "relation_type": "references",
                        "evidence_ids": [item["claim_id"] for item in selected_claims[-matched_count:]],
                        "provenance": {
                            "origin_artifact_id": "",
                            "origin_path": str(bundle["path"]),
                            "origin_section": "",
                            "source_url": "",
                            "retrieval_date": "2026-05-10",
                            "machine_id": "",
                            "session_id": "",
                            "support_kind": "synthetic_batch_promotion",
                            "grounding_status": "grounded",
                        },
                        "current_status": "promoted",
                    }
                )
            for artifact in payload.get("source_artifacts", []) or []:
                artifact_id = str(artifact.get("artifact_id", "")).strip()
                if artifact_id and artifact_id not in selected_artifacts:
                    selected_artifacts[artifact_id] = artifact

    observations: list[dict[str, Any]] = []
    for bundle in source_bundles:
        payload = bundle["payload"]
        for observation in payload.get("supporting_observations", []) or []:
            obs_id = str(observation.get("observation_id", "")).strip()
            if obs_id in selected_obs_ids:
                observations.append(observation)

    source_artifact_ids = sorted(selected_artifacts.keys())
    return {
        "bundle_kind": "groundrecall_query_bundle",
        "query_type": "concept",
        "concept": {
            "concept_id": f"concept::{concept_slug}",
            "title": label,
            "aliases": [],
            "description": f"Synthetic first-ring concept bundle promoted in batch for {label}.",
            "source_artifact_ids": source_artifact_ids,
            "current_status": "reviewed",
        },
        "relevant_claims": selected_claims[:12],
        "relations": relations[:12],
        "supporting_observations": observations[:12],
        "source_artifacts": list(selected_artifacts.values()),
        "related_concepts": list(selected_related.values()),
        "review_candidates": [],
        "suggested_next_actions": [
            f"Review the synthetic batch-promoted bundle for {label} and tighten claim selection if needed.",
            f"Promote stronger primary-source support for {label} if the current claim set remains thin.",
        ],
        "bundle_notes": [
            "Synthetic first-ring concept bundle generated from the first-ring batch promotion manifest.",
            f"Tier: {entry.get('_tier', 'unknown')}",
        ],
    }


def run_first_ring_batch_promotion(
    manifest_path: str | Path,
    canonical_dir: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    canonical = Path(canonical_dir)
    output = Path(output_dir) if output_dir else canonical
    output.mkdir(parents=True, exist_ok=True)
    bundle_index = _load_bundle_index(canonical)

    generated: list[dict[str, Any]] = []
    for entry in _tier_entries(manifest):
        concept_slug = str(entry["concept"]).strip()
        target_path = output / f"query_bundle__{concept_slug}.json"
        existing = _find_existing_bundle(bundle_index, concept_slug)
        if existing and existing["path"].resolve() == target_path.resolve():
            payload = existing["payload"]
            status = "existing"
        elif existing and not entry.get("compose_from"):
            payload = existing["payload"]
            target_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            status = "copied"
        else:
            payload = _build_synthetic_bundle(entry, canonical, bundle_index)
            target_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            status = "synthesized"
        generated.append(
            {
                "concept": concept_slug,
                "label": entry.get("label", concept_slug),
                "tier": entry.get("_tier", ""),
                "status": status,
                "bundle_path": str(target_path),
                "claim_count": len(payload.get("relevant_claims", []) or []),
                "related_concept_count": len(payload.get("related_concepts", []) or []),
            }
        )

    report = {
        "manifest_path": str(Path(manifest_path)),
        "canonical_dir": str(canonical),
        "output_dir": str(output),
        "generated": generated,
    }
    report_path = output / "first_ring_batch_promotion_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {"report_path": str(report_path), "generated_count": len(generated), "generated": generated}
