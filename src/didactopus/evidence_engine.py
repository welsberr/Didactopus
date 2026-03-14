from __future__ import annotations

from dataclasses import dataclass, field

from .adaptive_engine import LearnerProfile


DEFAULT_TYPE_WEIGHTS = {
    "explanation": 1.0,
    "problem": 1.0,
    "transfer": 1.0,
    "project": 1.0,
}


@dataclass
class EvidenceItem:
    concept_key: str
    evidence_type: str
    score: float
    is_recent: bool = False
    rubric_dimensions: dict[str, float] = field(default_factory=dict)


@dataclass
class ConceptEvidenceSummary:
    concept_key: str
    count: int = 0
    mean_score: float = 0.0
    weighted_mean_score: float = 0.0
    total_weight: float = 0.0
    confidence: float = 0.0
    dimension_means: dict[str, float] = field(default_factory=dict)
    aggregated: dict[str, float] = field(default_factory=dict)
    weak_dimensions: list[str] = field(default_factory=list)
    mastered: bool = False


@dataclass
class EvidenceState:
    summary_by_concept: dict[str, ConceptEvidenceSummary] = field(default_factory=dict)
    resurfaced_concepts: set[str] = field(default_factory=set)


def evidence_weight(
    item: EvidenceItem,
    type_weights: dict[str, float] | None = None,
    recent_multiplier: float = 1.0,
) -> float:
    weights = type_weights or DEFAULT_TYPE_WEIGHTS
    weight = weights.get(item.evidence_type, 1.0)
    if item.is_recent:
        weight *= recent_multiplier
    return weight


def confidence_from_weight(total_weight: float) -> float:
    if total_weight <= 0:
        return 0.0
    return total_weight / (total_weight + 1.0)


def add_evidence_item(state: EvidenceState, item: EvidenceItem) -> None:
    summary = state.summary_by_concept.setdefault(item.concept_key, ConceptEvidenceSummary(concept_key=item.concept_key))
    summary.count += 1
    summary.mean_score = ((summary.mean_score * (summary.count - 1)) + item.score) / summary.count


def ingest_evidence_bundle(
    profile: LearnerProfile,
    items: list[EvidenceItem],
    mastery_threshold: float = 0.8,
    resurfacing_threshold: float = 0.55,
    confidence_threshold: float = 0.0,
    type_weights: dict[str, float] | None = None,
    recent_multiplier: float = 1.0,
    dimension_thresholds: dict[str, float] | None = None,
) -> EvidenceState:
    state = EvidenceState()
    grouped: dict[str, list[EvidenceItem]] = {}
    for item in items:
        grouped.setdefault(item.concept_key, []).append(item)
        add_evidence_item(state, item)

    for concept_key, concept_items in grouped.items():
        summary = state.summary_by_concept[concept_key]
        total_weight = sum(evidence_weight(item, type_weights, recent_multiplier) for item in concept_items)
        weighted_score = sum(item.score * evidence_weight(item, type_weights, recent_multiplier) for item in concept_items)
        summary.total_weight = total_weight
        summary.weighted_mean_score = weighted_score / total_weight if total_weight else 0.0
        summary.confidence = confidence_from_weight(total_weight)

        dimension_values: dict[str, list[float]] = {}
        for item in concept_items:
            for dim, value in item.rubric_dimensions.items():
                dimension_values.setdefault(dim, []).append(value)
        summary.dimension_means = {
            dim: sum(values) / len(values)
            for dim, values in dimension_values.items()
        }
        summary.aggregated = dict(summary.dimension_means)

        weak_dimensions: list[str] = []
        if dimension_thresholds:
            for dim, threshold in dimension_thresholds.items():
                if dim in summary.dimension_means and summary.dimension_means[dim] < threshold:
                    weak_dimensions.append(dim)
        summary.weak_dimensions = weak_dimensions
        summary.mastered = (
            summary.weighted_mean_score >= mastery_threshold
            and summary.confidence >= confidence_threshold
            and not weak_dimensions
        )

        if summary.mastered:
            profile.mastered_concepts.add(concept_key)
            state.resurfaced_concepts.discard(concept_key)
        elif concept_key in profile.mastered_concepts and summary.weighted_mean_score < resurfacing_threshold:
            profile.mastered_concepts.discard(concept_key)
            state.resurfaced_concepts.add(concept_key)

    return state
