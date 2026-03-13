from dataclasses import dataclass, field

from .evaluator_pipeline import (
    LearnerAttempt,
    RubricEvaluator,
    CodeTestEvaluator,
    SymbolicRuleEvaluator,
    CritiqueEvaluator,
    PortfolioEvaluator,
    run_pipeline,
    aggregate,
)


@dataclass
class ConceptEvidenceSummary:
    concept_key: str
    weak_dimensions: list[str] = field(default_factory=list)
    mastered: bool = False
    aggregated: dict = field(default_factory=dict)
    evaluators: list[str] = field(default_factory=list)


@dataclass
class EvidenceState:
    summary_by_concept: dict[str, ConceptEvidenceSummary] = field(default_factory=dict)
    resurfaced_concepts: set[str] = field(default_factory=set)


@dataclass
class AgenticStudentState:
    learner_id: str = "demo-agent"
    display_name: str = "Demo Agentic Student"
    mastered_concepts: set[str] = field(default_factory=set)
    evidence_state: EvidenceState = field(default_factory=EvidenceState)
    attempt_history: list[dict] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)


def synthetic_attempt_for_concept(concept: str) -> LearnerAttempt:
    if "descriptive-statistics" in concept:
        return LearnerAttempt(
            concept=concept,
            artifact_type="explanation",
            content="Mean and variance summarize a dataset because they describe center and spread.",
            metadata={"deliverable_count": 1, "artifact_name": "descriptive_statistics_note.md"},
        )
    if "probability-basics" in concept:
        return LearnerAttempt(
            concept=concept,
            artifact_type="explanation",
            content="Conditional probability changes because context changes the sample space.",
            metadata={"deliverable_count": 1, "artifact_name": "probability_basics_note.md"},
        )
    if "prior" in concept:
        return LearnerAttempt(
            concept=concept,
            artifact_type="explanation",
            content="A prior is an assumption before evidence, but one limitation is bias.",
            metadata={"deliverable_count": 1, "artifact_name": "prior_reflection.md"},
        )
    if "posterior" in concept:
        return LearnerAttempt(
            concept=concept,
            artifact_type="symbolic",
            content="Therefore posterior = updated belief after evidence, but one assumption may be model fit.",
            metadata={"deliverable_count": 1, "artifact_name": "posterior_symbolic_note.md"},
        )
    return LearnerAttempt(
        concept=concept,
        artifact_type="critique",
        content="A weakness is hidden assumptions; a limitation is poor fit; uncertainty remains.",
        metadata={"deliverable_count": 2, "artifact_name": "critique_report.md"},
    )


def evaluator_set_for_attempt(attempt: LearnerAttempt):
    evaluators = [RubricEvaluator(), CritiqueEvaluator()]
    if attempt.artifact_type == "code":
        evaluators.append(CodeTestEvaluator())
    if attempt.artifact_type == "symbolic":
        evaluators.append(SymbolicRuleEvaluator())
    if attempt.artifact_type in {"project", "portfolio", "critique"}:
        evaluators.append(PortfolioEvaluator())
    return evaluators


def integrate_attempt(state: AgenticStudentState, attempt: LearnerAttempt) -> None:
    results = run_pipeline(attempt, evaluator_set_for_attempt(attempt))
    aggregated = aggregate(results)
    weak = [dim for dim, score in aggregated.items() if score < 0.75]
    mastered = len(aggregated) > 0 and all(score >= 0.75 for score in aggregated.values())

    summary = ConceptEvidenceSummary(
        concept_key=attempt.concept,
        weak_dimensions=weak,
        mastered=mastered,
        aggregated=aggregated,
        evaluators=[r.evaluator_name for r in results],
    )
    state.evidence_state.summary_by_concept[attempt.concept] = summary

    if mastered:
        state.mastered_concepts.add(attempt.concept)
        state.evidence_state.resurfaced_concepts.discard(attempt.concept)
    else:
        if attempt.concept in state.mastered_concepts:
            state.mastered_concepts.remove(attempt.concept)
            state.evidence_state.resurfaced_concepts.add(attempt.concept)

    state.attempt_history.append({
        "concept": attempt.concept,
        "artifact_type": attempt.artifact_type,
        "aggregated": aggregated,
        "weak_dimensions": weak,
        "mastered": mastered,
        "evaluators": [r.evaluator_name for r in results],
    })

    state.artifacts.append({
        "concept": attempt.concept,
        "artifact_type": attempt.artifact_type,
        "artifact_name": attempt.metadata.get("artifact_name", f"{attempt.concept}.txt"),
    })


def run_demo_agentic_loop(concepts: list[str]) -> AgenticStudentState:
    state = AgenticStudentState()
    for concept in concepts:
        attempt = synthetic_attempt_for_concept(concept)
        integrate_attempt(state, attempt)
    return state
