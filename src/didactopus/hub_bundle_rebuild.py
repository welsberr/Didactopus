from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .notebook_page import export_notebook_page_from_groundrecall_bundle


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _default_role(key: str, concept_id: str, title: str) -> str:
    joined = " ".join(part for part in (key, concept_id, title) if part).lower()
    if any(token in joined for token in ("plasticity", "epigenetic", "adaptation", "neutral", "chance", "selection-and-evolution", "adaptationism")):
        return "nuance"
    if any(token in joined for token in ("selection", "drift", "mutation", "population-genetics", "speciation", "testing-natural-selection")):
        return "mechanism"
    return "overview"


def _claim_distinction_payload(claim: dict[str, Any]) -> dict[str, Any] | None:
    text = str(claim.get("claim_text", "")).strip()
    lowered = text.lower()
    if not text:
        return None
    patterns = [
        ("non_implication", r"\bdoes not imply\b", "does not imply"),
        ("decoupling", r"\b(can|may)\s+occur\s+without\b|\bwithout leading to evolution\b", "without leading to evolution"),
        ("contrast", r"\bversus\b|\bvs\.?\b", "versus"),
        ("contrast", r"\brather than\b", "rather than"),
        ("contrast", r"\bdistinguish\b", "distinguish"),
        ("contrast", r"\bnot\b.+\bbut\b", "not ... but"),
        ("contrast", r"\bdoes not count as evolution\b", "does not count as evolution"),
    ]
    for distinction_type, pattern, cue in patterns:
        if re.search(pattern, lowered):
            return {
                "claim_id": claim.get("claim_id", ""),
                "distinction_type": distinction_type,
                "cue": cue,
                "text": text,
            }
    return None


def rebuild_hub_bundle_from_binding(binding_path: str | Path) -> dict[str, Any]:
    binding_file = Path(binding_path)
    binding = _load_json(binding_file)
    hub_path = (binding_file.parent / binding["primary_artifacts"]["groundrecall_query_bundle"]).resolve()
    page_path = (binding_file.parent / binding["primary_artifacts"]["notebook_page"]).resolve()
    hub = _load_json(hub_path)

    support_map = binding.get("supporting_artifacts", {}) or {}
    support_entries: list[tuple[str, Path]] = []
    for key, rel in support_map.items():
        if not key.endswith("_bundle"):
            continue
        support_entries.append((key, (binding_file.parent / rel).resolve()))

    artifact_by_id: dict[str, dict[str, Any]] = {}
    observation_rows: list[dict[str, Any]] = []
    related_by_id: dict[str, dict[str, Any]] = {}
    source_role_summary: Counter[str] = Counter()
    distinctions: list[dict[str, Any]] = []
    seen_obs_text: set[str] = set()

    for key, path in support_entries:
        if not path.exists():
            continue
        payload = _load_json(path)
        concept = payload.get("concept", {}) or {}
        concept_id = str(concept.get("concept_id", "")).strip()
        title = str(concept.get("title", "")).strip()
        role = _default_role(key, concept_id, title)
        source_role_summary[role] += 1

        if concept_id and concept_id != str(hub.get("concept", {}).get("concept_id", "")).strip():
            related_by_id[concept_id] = {
                "id": concept_id,
                "label": title or concept_id.replace("concept::", "", 1).replace("-", " ").title(),
            }

        for artifact in payload.get("source_artifacts", []) or []:
            artifact_id = str(artifact.get("artifact_id", "")).strip()
            if not artifact_id:
                continue
            merged = dict(artifact)
            merged["source_role"] = merged.get("source_role") or role
            artifact_by_id[artifact_id] = merged

        for obs in payload.get("supporting_observations", [])[:2]:
            text = str(obs.get("text", "")).strip()
            if not text or text in seen_obs_text:
                continue
            seen_obs_text.add(text)
            merged = dict(obs)
            merged["artifact_id"] = merged.get("artifact_id") or next(iter(concept.get("source_artifact_ids", []) or []), "")
            merged["source_role"] = merged.get("source_role") or role
            observation_rows.append(merged)

        for claim in payload.get("relevant_claims", []) or []:
            distinction = _claim_distinction_payload(claim)
            if distinction is not None:
                distinctions.append(distinction)

    existing_related = hub.get("related_concepts", []) or []
    for item in existing_related:
        concept_id = str(item.get("id", "") or item.get("concept_id", "")).strip()
        label = str(item.get("label", "") or item.get("title", "")).strip()
        if concept_id:
            related_by_id.setdefault(concept_id, {"id": concept_id, "label": label})

    hub["source_artifacts"] = list(artifact_by_id.values())
    hub["supporting_observations"] = observation_rows[:12]
    hub["source_role_summary"] = dict(sorted(source_role_summary.items()))
    hub["key_distinctions"] = distinctions[:6]
    hub["related_concepts"] = list(related_by_id.values())
    notes = hub.get("bundle_notes", []) or []
    note = "Supporting source artifacts and source-role summaries were rebuilt deterministically from the hub binding manifest."
    if note not in notes:
        notes.append(note)
    hub["bundle_notes"] = notes
    hub_path.write_text(json.dumps(hub, indent=2), encoding="utf-8")

    page_summary = export_notebook_page_from_groundrecall_bundle(hub_path, page_path)
    return {
        "hub_bundle_path": str(hub_path),
        "notebook_page_path": str(page_path),
        "source_artifact_count": len(hub["source_artifacts"]),
        "supporting_observation_count": len(hub["supporting_observations"]),
        "source_role_summary": hub["source_role_summary"],
        "distinction_count": len(hub["key_distinctions"]),
        "page_summary": page_summary["page"]["summary"],
    }
