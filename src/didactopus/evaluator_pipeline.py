from dataclasses import dataclass, field


@dataclass
class LearnerAttempt:
    concept: str
    artifact_type: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class EvaluatorResult:
    evaluator_name: str
    dimensions: dict
    passed: bool | None = None
    notes: str = ""


class RubricEvaluator:
    name = "rubric"

    def evaluate(self, attempt: LearnerAttempt):
        explanation = 0.85 if len(attempt.content.strip()) > 40 else 0.55
        correctness = 0.80 if "because" in attempt.content.lower() or "therefore" in attempt.content.lower() else 0.65
        return EvaluatorResult(
            self.name,
            {"correctness": correctness, "explanation": explanation},
            notes="Heuristic scaffold rubric score.",
        )


class CodeTestEvaluator:
    name = "code_test"

    def evaluate(self, attempt: LearnerAttempt):
        passed = "return" in attempt.content or "assert" in attempt.content
        score = 0.9 if passed else 0.35
        return EvaluatorResult(
            self.name,
            {"correctness": score, "project_execution": score},
            passed=passed,
            notes="Stub code/test evaluator.",
        )


class SymbolicRuleEvaluator:
    name = "symbolic_rule"

    def evaluate(self, attempt: LearnerAttempt):
        passed = "=" in attempt.content or "therefore" in attempt.content.lower()
        score = 0.88 if passed else 0.4
        return EvaluatorResult(
            self.name,
            {"correctness": score},
            passed=passed,
            notes="Stub symbolic evaluator.",
        )


class CritiqueEvaluator:
    name = "critique"

    def evaluate(self, attempt: LearnerAttempt):
        markers = ["assumption", "bias", "limitation", "weakness", "uncertain"]
        found = sum(m in attempt.content.lower() for m in markers)
        score = min(1.0, 0.35 + 0.15 * found)
        return EvaluatorResult(
            self.name,
            {"critique": score},
            notes="Stub critique evaluator.",
        )


class PortfolioEvaluator:
    name = "portfolio"

    def evaluate(self, attempt: LearnerAttempt):
        deliverable_count = int(attempt.metadata.get("deliverable_count", 1))
        score = min(1.0, 0.5 + 0.1 * deliverable_count)
        return EvaluatorResult(
            self.name,
            {"project_execution": score, "transfer": max(0.4, score - 0.1)},
            notes="Stub portfolio evaluator.",
        )


def run_pipeline(attempt, evaluators):
    return [e.evaluate(attempt) for e in evaluators]


def aggregate(results):
    totals = {}
    counts = {}
    for r in results:
        for dim, val in r.dimensions.items():
            totals[dim] = totals.get(dim, 0.0) + val
            counts[dim] = counts.get(dim, 0) + 1
    return {dim: totals[dim] / counts[dim] for dim in totals}
