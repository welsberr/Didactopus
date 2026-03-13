from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .adaptive_engine import LearnerProfile

EvidenceType = Literal["explanation", "problem", "project", "transfer"]


@dataclass
class EvidenceItem:
    concept_key: str
    evidence_type: EvidenceType
    score: float
    notes: str = ""


@dataclass
class ConceptEvidenceSummary:
    concept_key: str
    count: int = 0
    mean_score: float = 0.0


@dataclass
class EvidenceState:
    evidence_by_concept: dict[str, list[EvidenceItem]] = field(default_factory=dict)
    summary_by_concept: dict[str, ConceptEvidenceSummary] = field(default_factory=dict)
    resurfaced_concepts: set[str] = field(default_factory=set)


def clamp_score(score: float) -> float:
    return max(0.0, min(1.0, score))


def add_evidence_item(state: EvidenceState, item: EvidenceItem) -> None:
    item.score = clamp_score(item.score)
    state.evidence_by_concept.setdefault(item.concept_key, []).append(item)
    items = state.evidence_by_concept[item.concept_key]
    mean_score = sum(x.score for x in items) / len(items)
    state.summary_by_concept[item.concept_key] = ConceptEvidenceSummary(
        concept_key=item.concept_key,
        count=len(items),
        mean_score=mean_score,
    )


def update_profile_mastery_from_evidence(
    profile: LearnerProfile,
    state: EvidenceState,
    mastery_threshold: float,
    resurfacing_threshold: float,
) -> None:
    for concept_key, summary in state.summary_by_concept.items():
        if summary.count == 0:
            continue
        if summary.mean_score >= mastery_threshold:
            profile.mastered_concepts.add(concept_key)
            if concept_key in state.resurfaced_concepts:
                state.resurfaced_concepts.remove(concept_key)
        elif concept_key in profile.mastered_concepts and summary.mean_score < resurfacing_threshold:
            profile.mastered_concepts.remove(concept_key)
            state.resurfaced_concepts.add(concept_key)


def ingest_evidence_bundle(
    profile: LearnerProfile,
    items: list[EvidenceItem],
    mastery_threshold: float,
    resurfacing_threshold: float,
) -> EvidenceState:
    state = EvidenceState()
    for item in items:
        add_evidence_item(state, item)
    update_profile_mastery_from_evidence(
        profile=profile,
        state=state,
        mastery_threshold=mastery_threshold,
        resurfacing_threshold=resurfacing_threshold,
    )
    return state
