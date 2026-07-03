from __future__ import annotations

from hashlib import sha256
import yaml
from pathlib import Path

from ..artifact_schemas import ConceptsFile, RoadmapFile
from .base import DiscoveredImportSource, StructuredImportRows, register_source_adapter


class DidactopusPackSourceAdapter:
    name = "didactopus_pack"

    def detect(self, root: str | Path) -> bool:
        base = Path(root)
        required = {"pack.yaml", "concepts.yaml"}
        return required.issubset({path.name for path in base.iterdir() if path.exists()})

    def discover(self, root: str | Path) -> list[DiscoveredImportSource]:
        base = Path(root)
        rows: list[DiscoveredImportSource] = []
        for filename in ["pack.yaml", "concepts.yaml", "roadmap.yaml", "projects.yaml", "rubrics.yaml", "review_ledger.json"]:
            path = base / filename
            if not path.exists():
                continue
            rows.append(
                DiscoveredImportSource(
                    path=path,
                    relative_path=path.relative_to(base).as_posix(),
                    source_kind="didactopus_pack",
                    artifact_kind="didactopus_pack_artifact",
                    is_text=True,
                    metadata={},
                )
            )
        return rows

    def import_intent(self) -> str:
        return "both"

    def build_rows(self, context, sources: list[DiscoveredImportSource]) -> StructuredImportRows | None:
        by_name = {Path(item.relative_path).name: item for item in sources}
        concepts_src = by_name.get("concepts.yaml")
        if concepts_src is None:
            return None

        pack_src = by_name.get("pack.yaml")
        pack_payload = {}
        if pack_src is not None:
            pack_payload = yaml.safe_load(pack_src.path.read_text(encoding="utf-8")) or {}
        concepts_payload = ConceptsFile.model_validate(
            yaml.safe_load(concepts_src.path.read_text(encoding="utf-8")) or {"concepts": []}
        )
        roadmap_payload = None
        roadmap_src = by_name.get("roadmap.yaml")
        if roadmap_src is not None:
            roadmap_payload = RoadmapFile.model_validate(
                yaml.safe_load(roadmap_src.path.read_text(encoding="utf-8")) or {"stages": []}
            )

        artifact_rows: list[dict] = []
        observation_rows: list[dict] = []
        claim_rows: list[dict] = []
        concept_rows: list[dict] = []
        relation_rows: list[dict] = []

        for source in sources:
            artifact_rows.append(
                {
                    "artifact_id": f"ia_{sha256(source.relative_path.encode('utf-8')).hexdigest()[:12]}",
                    "import_id": context.import_id,
                    "artifact_kind": source.artifact_kind,
                    "path": source.relative_path,
                    "title": source.path.stem,
                    "sha256": sha256(source.path.read_bytes()).hexdigest(),
                    "created_at": context.imported_at,
                    "metadata": {"source_kind": source.source_kind},
                    "current_status": "draft",
                }
            )

        pack_name = pack_payload.get("name", Path(context.source_root).name)
        concepts_artifact_id = next(
            (row["artifact_id"] for row in artifact_rows if row["path"] == concepts_src.relative_path),
            "",
        )

        for index, concept in enumerate(concepts_payload.concepts, start=1):
            concept_key = f"concept::{concept.id}"
            concept_rows.append(
                {
                    "concept_id": concept_key,
                    "import_id": context.import_id,
                    "title": concept.title,
                    "aliases": [],
                    "description": concept.description or f"Imported concept from Didactopus pack {pack_name}.",
                    "source_artifact_ids": [concepts_artifact_id] if concepts_artifact_id else [],
                    "current_status": "triaged",
                }
            )
            observation_id = f"obs_pack_{concept.id}_{index}"
            observation_rows.append(
                {
                    "observation_id": observation_id,
                    "import_id": context.import_id,
                    "artifact_id": concepts_artifact_id,
                    "role": "summary",
                    "text": concept.description or concept.title,
                    "origin_path": concepts_src.relative_path,
                    "origin_section": concept.title,
                    "line_start": 0,
                    "line_end": 0,
                    "grounding_status": "grounded",
                    "support_kind": "direct_source",
                    "confidence_hint": 0.85,
                    "current_status": "draft",
                }
            )
            claim_rows.append(
                {
                    "claim_id": f"clm_pack_{concept.id}",
                    "import_id": context.import_id,
                    "claim_text": concept.description or f"{concept.title} is a concept in pack {pack_name}.",
                    "claim_kind": "summary",
                    "source_observation_ids": [observation_id],
                    "supporting_fragment_ids": [],
                    "concept_ids": [concept_key],
                    "contradicts_claim_ids": [],
                    "supersedes_claim_ids": [],
                    "confidence_hint": 0.85,
                    "grounding_status": "grounded",
                    "current_status": "triaged",
                }
            )
            for prereq in concept.prerequisites:
                relation_rows.append(
                    {
                        "relation_id": f"rel_prereq_{concept.id}_{prereq}",
                        "import_id": context.import_id,
                        "source_id": f"concept::{prereq}",
                        "target_id": concept_key,
                        "relation_type": "prerequisite",
                        "evidence_ids": [f"clm_pack_{concept.id}"],
                        "current_status": "draft",
                    }
                )
            for signal_idx, signal in enumerate(concept.mastery_signals, start=1):
                signal_obs_id = f"obs_signal_{concept.id}_{signal_idx}"
                observation_rows.append(
                    {
                        "observation_id": signal_obs_id,
                        "import_id": context.import_id,
                        "artifact_id": concepts_artifact_id,
                        "role": "summary",
                        "text": signal,
                        "origin_path": concepts_src.relative_path,
                        "origin_section": f"{concept.title} mastery signal",
                        "line_start": 0,
                        "line_end": 0,
                        "grounding_status": "grounded",
                        "support_kind": "direct_source",
                        "confidence_hint": 0.8,
                        "current_status": "draft",
                    }
                )
                claim_rows.append(
                    {
                        "claim_id": f"clm_signal_{concept.id}_{signal_idx}",
                        "import_id": context.import_id,
                        "claim_text": signal,
                        "claim_kind": "mastery_signal",
                        "source_observation_ids": [signal_obs_id],
                        "supporting_fragment_ids": [],
                        "concept_ids": [concept_key],
                        "contradicts_claim_ids": [],
                        "supersedes_claim_ids": [],
                        "confidence_hint": 0.8,
                        "grounding_status": "grounded",
                        "current_status": "triaged",
                    }
                )

        if roadmap_payload is not None and roadmap_src is not None:
            roadmap_artifact_id = next(
                (row["artifact_id"] for row in artifact_rows if row["path"] == roadmap_src.relative_path),
                "",
            )
            for stage in roadmap_payload.stages:
                for concept_id in stage.concepts:
                    observation_id = f"obs_stage_{stage.id}_{concept_id}"
                    observation_rows.append(
                        {
                            "observation_id": observation_id,
                            "import_id": context.import_id,
                            "artifact_id": roadmap_artifact_id,
                            "role": "summary",
                            "text": f"{concept_id} appears in roadmap stage {stage.title}.",
                            "origin_path": roadmap_src.relative_path,
                            "origin_section": stage.title,
                            "line_start": 0,
                            "line_end": 0,
                            "grounding_status": "grounded",
                            "support_kind": "direct_source",
                            "confidence_hint": 0.75,
                            "current_status": "draft",
                        }
                    )
                    claim_rows.append(
                        {
                            "claim_id": f"clm_stage_{stage.id}_{concept_id}",
                            "import_id": context.import_id,
                            "claim_text": f"{concept_id} belongs to roadmap stage {stage.title}.",
                            "claim_kind": "roadmap_stage",
                            "source_observation_ids": [observation_id],
                            "supporting_fragment_ids": [],
                            "concept_ids": [f"concept::{concept_id}"],
                            "contradicts_claim_ids": [],
                            "supersedes_claim_ids": [],
                            "confidence_hint": 0.75,
                            "grounding_status": "grounded",
                            "current_status": "triaged",
                        }
                    )

        return StructuredImportRows(
            artifact_rows=artifact_rows,
            observation_rows=observation_rows,
            claim_rows=claim_rows,
            concept_rows=concept_rows,
            relation_rows=relation_rows,
        )


register_source_adapter(DidactopusPackSourceAdapter())
