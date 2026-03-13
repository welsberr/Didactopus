from __future__ import annotations

from dataclasses import dataclass, field

from .planner import rank_next_concepts, PlannerWeights
from .evidence_engine import EvidenceState, ConceptEvidenceSummary


@dataclass
class AgenticStudentState:
    mastered_concepts: set[str] = field(default_factory=set)
    evidence_state: EvidenceState = field(default_factory=EvidenceState)
    attempt_history: list[dict] = field(default_factory=list)


def synthetic_attempt_for_concept(concept: str) -> dict:
    if "descriptive-statistics" in concept:
        weak = []
        mastered = True
    elif "probability-basics" in concept:
        weak = ["transfer"]
        mastered = False
    elif "prior" in concept:
        weak = ["explanation", "transfer"]
        mastered = False
    elif "posterior" in concept:
        weak = ["critique", "transfer"]
        mastered = False
    elif "model-checking" in concept:
        weak = ["critique"]
        mastered = False
    else:
        weak = ["correctness"]
        mastered = False

    return {"concept": concept, "mastered": mastered, "weak_dimensions": weak}


def integrate_attempt(state: AgenticStudentState, attempt: dict) -> None:
    concept = attempt["concept"]
    summary = ConceptEvidenceSummary(
        concept_key=concept,
        weak_dimensions=list(attempt["weak_dimensions"]),
        mastered=bool(attempt["mastered"]),
    )
    state.evidence_state.summary_by_concept[concept] = summary
    if summary.mastered:
        state.mastered_concepts.add(concept)
        state.evidence_state.resurfaced_concepts.discard(concept)
    else:
        if concept in state.mastered_concepts:
            state.mastered_concepts.remove(concept)
            state.evidence_state.resurfaced_concepts.add(concept)
    state.attempt_history.append(attempt)


def run_agentic_learning_loop(
    graph,
    project_catalog: list[dict],
    target_concepts: list[str],
    weights: PlannerWeights,
    max_steps: int = 5,
) -> AgenticStudentState:
    state = AgenticStudentState()

    for _ in range(max_steps):
        weak_dimensions_by_concept = {
            key: summary.weak_dimensions
            for key, summary in state.evidence_state.summary_by_concept.items()
        }
        fragile = set(state.evidence_state.resurfaced_concepts)

        ranked = rank_next_concepts(
            graph=graph,
            mastered=state.mastered_concepts,
            targets=target_concepts,
            weak_dimensions_by_concept=weak_dimensions_by_concept,
            fragile_concepts=fragile,
            project_catalog=project_catalog,
            weights=weights,
        )
        if not ranked:
            break

        chosen = ranked[0]["concept"]
        attempt = synthetic_attempt_for_concept(chosen)
        integrate_attempt(state, attempt)

        if all(target in state.mastered_concepts for target in target_concepts):
            break

    return state
