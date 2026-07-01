from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .groundrecall_discovery import DiscoveredArtifact
from .groundrecall_segmenter import SegmentedPage, SegmentedObservation


@dataclass
class ImportContext:
    import_id: str
    import_mode: str
    machine_id: str
    agent_id: str
    source_root: str
    imported_at: str


def _sanitize_claim_key(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return text or "claim"


def _claim_id_for_observation(observation_record: dict[str, Any], observation: SegmentedObservation, index: int) -> str:
    if observation.explicit_claim_key:
        return f"clm_{_sanitize_claim_key(observation.explicit_claim_key)}"
    return f"clm_{observation_record['observation_id']}_{index}"


def build_artifact_record(context: ImportContext, artifact: DiscoveredArtifact, page: SegmentedPage | None) -> dict[str, Any]:
    record = {
        "artifact_id": f"ia_{sha256(artifact.relative_path.encode('utf-8')).hexdigest()[:12]}",
        "import_id": context.import_id,
        "artifact_kind": artifact.artifact_kind,
        "path": artifact.relative_path,
        "title": page.title if page else Path(artifact.relative_path).stem,
        "sha256": sha256(artifact.path.read_bytes()).hexdigest(),
        "created_at": context.imported_at,
        "metadata": {
            "frontmatter": page.frontmatter if page else {},
            "headings": page.headings if page else [],
        },
        "current_status": "draft",
    }
    return record


def build_observation_record(
    context: ImportContext,
    artifact_record: dict[str, Any],
    observation: SegmentedObservation,
    index: int,
) -> dict[str, Any]:
    return {
        "observation_id": f"obs_{artifact_record['artifact_id']}_{index}",
        "import_id": context.import_id,
        "artifact_id": artifact_record["artifact_id"],
        "role": observation.role,
        "text": observation.text,
        "origin_path": observation.artifact_relative_path,
        "origin_section": observation.section,
        "line_start": observation.line_start,
        "line_end": observation.line_end,
        "grounding_status": observation.grounding_status,
        "support_kind": observation.support_kind,
        "confidence_hint": observation.confidence_hint,
        "current_status": "draft",
    }


def build_claim_record(
    context: ImportContext,
    observation_record: dict[str, Any],
    observation: SegmentedObservation,
    concept_ids: list[str],
    index: int,
) -> dict[str, Any]:
    return {
        "claim_id": _claim_id_for_observation(observation_record, observation, index),
        "import_id": context.import_id,
        "claim_text": observation_record["text"],
        "claim_kind": "statement" if observation_record["role"] == "claim" else "summary",
        "source_observation_ids": [observation_record["observation_id"]],
        "supporting_fragment_ids": [],
        "concept_ids": [f"concept::{concept_id}" for concept_id in concept_ids],
        "contradicts_claim_ids": [f"clm_{_sanitize_claim_key(value)}" for value in observation.contradict_keys],
        "supersedes_claim_ids": [f"clm_{_sanitize_claim_key(value)}" for value in observation.supersede_keys],
        "confidence_hint": observation_record["confidence_hint"],
        "grounding_status": observation_record["grounding_status"],
        "current_status": "triaged" if observation_record["grounding_status"] != "ungrounded" else "draft",
    }


def build_concept_records(context: ImportContext, artifact_record: dict[str, Any], concept_ids: list[str]) -> list[dict[str, Any]]:
    records = []
    for concept_id in concept_ids:
        records.append(
            {
                "concept_id": f"concept::{concept_id}",
                "import_id": context.import_id,
                "title": concept_id.replace("-", " ").title(),
                "aliases": [],
                "description": "Imported concept from llmwiki corpus.",
                "source_artifact_ids": [artifact_record["artifact_id"]],
                "current_status": "triaged",
            }
        )
    return records


def build_relation_records(context: ImportContext, artifact_record: dict[str, Any], concept_ids: list[str], links: list[str]) -> list[dict[str, Any]]:
    if not concept_ids:
        return []
    primary = f"concept::{concept_ids[0]}"
    records = []
    for idx, link in enumerate(links, start=1):
        target = f"concept::{link.lower().replace(' ', '-')}"
        records.append(
            {
                "relation_id": f"rel_{artifact_record['artifact_id']}_{idx}",
                "import_id": context.import_id,
                "source_id": primary,
                "target_id": target,
                "relation_type": "references",
                "evidence_ids": [],
                "current_status": "draft",
            }
        )
    return records


def manifest_record(context: ImportContext) -> dict[str, Any]:
    return asdict(context) | {"source_repo_kind": "llmwiki"}
