from __future__ import annotations

"""Legacy flat GroundRecall store module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.store`` for new code.
"""

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .groundrecall_models import (
    ArtifactRecord,
    ClaimRecord,
    ConceptRecord,
    FragmentRecord,
    GroundRecallSnapshot,
    ObservationRecord,
    PromotionRecord,
    RelationRecord,
    ReviewCandidateRecord,
    SourceRecord,
)


ModelT = TypeVar("ModelT", bound=BaseModel)


class GroundRecallStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "sources"
        self.fragments_dir = self.base_dir / "fragments"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.observations_dir = self.base_dir / "observations"
        self.claims_dir = self.base_dir / "claims"
        self.concepts_dir = self.base_dir / "concepts"
        self.relations_dir = self.base_dir / "relations"
        self.review_candidates_dir = self.base_dir / "review_candidates"
        self.promotions_dir = self.base_dir / "promotions"
        self.snapshots_dir = self.base_dir / "snapshots"
        for path in [
            self.sources_dir,
            self.fragments_dir,
            self.artifacts_dir,
            self.observations_dir,
            self.claims_dir,
            self.concepts_dir,
            self.relations_dir,
            self.review_candidates_dir,
            self.promotions_dir,
            self.snapshots_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def _save(self, directory: Path, key: str, model: BaseModel) -> None:
        (directory / f"{key}.json").write_text(model.model_dump_json(indent=2), encoding="utf-8")

    def _load(self, directory: Path, key: str, model_type: type[ModelT]) -> ModelT | None:
        path = directory / f"{key}.json"
        if not path.exists():
            return None
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))

    def _list(self, directory: Path, model_type: type[ModelT]) -> list[ModelT]:
        items: list[ModelT] = []
        for path in sorted(directory.glob("*.json")):
            items.append(model_type.model_validate_json(path.read_text(encoding="utf-8")))
        return items

    def save_source(self, record: SourceRecord) -> SourceRecord:
        self._save(self.sources_dir, record.source_id, record)
        return record

    def get_source(self, source_id: str) -> SourceRecord | None:
        return self._load(self.sources_dir, source_id, SourceRecord)

    def list_sources(self) -> list[SourceRecord]:
        return self._list(self.sources_dir, SourceRecord)

    def save_fragment(self, record: FragmentRecord) -> FragmentRecord:
        self._save(self.fragments_dir, record.fragment_id, record)
        return record

    def get_fragment(self, fragment_id: str) -> FragmentRecord | None:
        return self._load(self.fragments_dir, fragment_id, FragmentRecord)

    def list_fragments(self) -> list[FragmentRecord]:
        return self._list(self.fragments_dir, FragmentRecord)

    def save_artifact(self, record: ArtifactRecord) -> ArtifactRecord:
        self._save(self.artifacts_dir, record.artifact_id, record)
        return record

    def get_artifact(self, artifact_id: str) -> ArtifactRecord | None:
        return self._load(self.artifacts_dir, artifact_id, ArtifactRecord)

    def list_artifacts(self) -> list[ArtifactRecord]:
        return self._list(self.artifacts_dir, ArtifactRecord)

    def save_observation(self, record: ObservationRecord) -> ObservationRecord:
        self._save(self.observations_dir, record.observation_id, record)
        return record

    def get_observation(self, observation_id: str) -> ObservationRecord | None:
        return self._load(self.observations_dir, observation_id, ObservationRecord)

    def list_observations(self) -> list[ObservationRecord]:
        return self._list(self.observations_dir, ObservationRecord)

    def save_claim(self, record: ClaimRecord) -> ClaimRecord:
        self._save(self.claims_dir, record.claim_id, record)
        return record

    def get_claim(self, claim_id: str) -> ClaimRecord | None:
        return self._load(self.claims_dir, claim_id, ClaimRecord)

    def list_claims(self) -> list[ClaimRecord]:
        return self._list(self.claims_dir, ClaimRecord)

    def save_concept(self, record: ConceptRecord) -> ConceptRecord:
        self._save(self.concepts_dir, record.concept_id.replace("::", "__"), record)
        return record

    def get_concept(self, concept_id: str) -> ConceptRecord | None:
        return self._load(self.concepts_dir, concept_id.replace("::", "__"), ConceptRecord)

    def list_concepts(self) -> list[ConceptRecord]:
        return self._list(self.concepts_dir, ConceptRecord)

    def save_relation(self, record: RelationRecord) -> RelationRecord:
        self._save(self.relations_dir, record.relation_id, record)
        return record

    def get_relation(self, relation_id: str) -> RelationRecord | None:
        return self._load(self.relations_dir, relation_id, RelationRecord)

    def list_relations(self) -> list[RelationRecord]:
        return self._list(self.relations_dir, RelationRecord)

    def save_review_candidate(self, record: ReviewCandidateRecord) -> ReviewCandidateRecord:
        self._save(self.review_candidates_dir, record.review_candidate_id, record)
        return record

    def get_review_candidate(self, review_candidate_id: str) -> ReviewCandidateRecord | None:
        return self._load(self.review_candidates_dir, review_candidate_id, ReviewCandidateRecord)

    def list_review_candidates(self) -> list[ReviewCandidateRecord]:
        return self._list(self.review_candidates_dir, ReviewCandidateRecord)

    def save_promotion(self, record: PromotionRecord) -> PromotionRecord:
        self._save(self.promotions_dir, record.promotion_id, record)
        return record

    def get_promotion(self, promotion_id: str) -> PromotionRecord | None:
        return self._load(self.promotions_dir, promotion_id, PromotionRecord)

    def list_promotions(self) -> list[PromotionRecord]:
        return self._list(self.promotions_dir, PromotionRecord)

    def save_snapshot(self, snapshot: GroundRecallSnapshot) -> GroundRecallSnapshot:
        self._save(self.snapshots_dir, snapshot.snapshot_id, snapshot)
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> GroundRecallSnapshot | None:
        return self._load(self.snapshots_dir, snapshot_id, GroundRecallSnapshot)

    def list_snapshots(self) -> list[GroundRecallSnapshot]:
        return self._list(self.snapshots_dir, GroundRecallSnapshot)

    def build_snapshot(self, snapshot_id: str, created_at: str, metadata: dict | None = None) -> GroundRecallSnapshot:
        return GroundRecallSnapshot(
            snapshot_id=snapshot_id,
            created_at=created_at,
            sources=self.list_sources(),
            fragments=self.list_fragments(),
            artifacts=self.list_artifacts(),
            observations=self.list_observations(),
            claims=self.list_claims(),
            concepts=self.list_concepts(),
            relations=self.list_relations(),
            promotions=self.list_promotions(),
            metadata=metadata or {},
        )
