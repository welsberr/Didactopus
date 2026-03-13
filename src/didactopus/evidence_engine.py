from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .adaptive_engine import LearnerProfile

EvidenceType = Literal["explanation", "problem", "project", "transfer"]
MASTERY_DIMENSIONS = ["correctness", "explanation", "transfer", "project_execution", "critique"]


@dataclass
class EvidenceItem:
    concept_key: str
    evidence_type: EvidenceType
    score: float
    notes: str = ""
    is_recent: bool = False
    rubric_dimensions: dict[str, float] = field(default_factory=dict)


@dataclass
class ConceptEvidenceSummary:
    concept_key: str
    count: int = 0
    weighted_mean_score: float = 0.0
    total_weight: float = 0.0
    confidence: float = 0.0
    dimension_means: dict[str, float] = field(default_factory=dict)
    weak_dimensions: list[str] = field(default_factory=list)
    mastered: bool = False


@dataclass
class EvidenceState:
    evidence_by_concept: dict[str, list[EvidenceItem]] = field(default_factory=dict)
    summary_by_concept: dict[str, ConceptEvidenceSummary] = field(default_factory=dict)
    resurfaced_concepts: set[str] = field(default_factory=set)


def clamp_score(score: float) -> float:
    return max(0.0, min(1.0, score))


def evidence_weight(item: EvidenceItem, type_weights: dict[str, float], recent_multiplier: float) -> float:
    base = type_weights.get(item.evidence_type, 1.0)
    return base * (recent_multiplier if item.is_recent else 1.0)


def confidence_from_weight(total_weight: float) -> float:
    return total_weight / (total_weight + 1.0) if total_weight > 0 else 0.0


def recompute_concept_summary(
    concept_key: str,
    items: list[EvidenceItem],
    type_weights: dict[str, float],
    recent_multiplier: float,
    dimension_thresholds: dict[str, float],
    confidence_threshold: float,
) -> ConceptEvidenceSummary:
    weighted_score_sum = 0.0
    total_weight = 0.0
    dim_totals: dict[str, float] = {}
    dim_weights: dict[str, float] = {}

    for item in items:
        item.score = clamp_score(item.score)
        w = evidence_weight(item, type_weights, recent_multiplier)
        weighted_score_sum += item.score * w
        total_weight += w

        for dim, value in item.rubric_dimensions.items():
            v = clamp_score(value)
            dim_totals[dim] = dim_totals.get(dim, 0.0) + v * w
            dim_weights[dim] = dim_weights.get(dim, 0.0) + w

    dimension_means = {
        dim: dim_totals[dim] / dim_weights[dim]
        for dim in dim_totals
        if dim_weights[dim] > 0
    }
    confidence = confidence_from_weight(total_weight)

    weak_dimensions = []
    for dim, threshold in dimension_thresholds.items():
        if dim in dimension_means and dimension_means[dim] < threshold:
            weak_dimensions.append(dim)

    mastered = (
        confidence >= confidence_threshold
        and all(
            (dim in dimension_means and dimension_means[dim] >= threshold)
            for dim, threshold in dimension_thresholds.items()
            if dim in dimension_means
        )
        and len(dimension_means) > 0
    )

    return ConceptEvidenceSummary(
        concept_key=concept_key,
        count=len(items),
        weighted_mean_score=(weighted_score_sum / total_weight) if total_weight > 0 else 0.0,
        total_weight=total_weight,
        confidence=confidence,
        dimension_means=dimension_means,
        weak_dimensions=sorted(weak_dimensions),
        mastered=mastered,
    )


def add_evidence_item(
    state: EvidenceState,
    item: EvidenceItem,
    type_weights: dict[str, float],
    recent_multiplier: float,
    dimension_thresholds: dict[str, float],
    confidence_threshold: float,
) -> None:
    item.score = clamp_score(item.score)
    state.evidence_by_concept.setdefault(item.concept_key, []).append(item)
    state.summary_by_concept[item.concept_key] = recompute_concept_summary(
        item.concept_key,
        state.evidence_by_concept[item.concept_key],
        type_weights,
        recent_multiplier,
        dimension_thresholds,
        confidence_threshold,
    )


def update_profile_mastery_from_evidence(
    profile: LearnerProfile,
    state: EvidenceState,
    resurfacing_threshold: float,
) -> None:
    for concept_key, summary in state.summary_by_concept.items():
        if summary.mastered:
            profile.mastered_concepts.add(concept_key)
            state.resurfaced_concepts.discard(concept_key)
        elif concept_key in profile.mastered_concepts and summary.weighted_mean_score < resurfacing_threshold:
            profile.mastered_concepts.remove(concept_key)
            state.resurfaced_concepts.add(concept_key)


def ingest_evidence_bundle(
    profile: LearnerProfile,
    items: list[EvidenceItem],
    resurfacing_threshold: float,
    confidence_threshold: float,
    type_weights: dict[str, float],
    recent_multiplier: float,
    dimension_thresholds: dict[str, float],
) -> EvidenceState:
    state = EvidenceState()
    for item in items:
        add_evidence_item(
            state,
            item,
            type_weights,
            recent_multiplier,
            dimension_thresholds,
            confidence_threshold,
        )
    update_profile_mastery_from_evidence(
        profile=profile,
        state=state,
        resurfacing_threshold=resurfacing_threshold,
    )
    return state
