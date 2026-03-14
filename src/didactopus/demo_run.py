from __future__ import annotations
from pathlib import Path
import json, yaml
from .learner_state import LearnerState
from .orchestration_models import LearnerProfile, StopCriteria
from .onboarding import build_initial_run_state, build_first_session_plan
from .orchestrator import run_learning_cycle, apply_demo_evidence

def load_concepts(path: str | Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return list(data.get("concepts", []) or [])

def main():
    base = Path(__file__).resolve().parents[2] / "samples"
    concepts = load_concepts(base / "concepts.yaml")

    profile = LearnerProfile(
        learner_id="demo-learner",
        display_name="Demo Learner",
        target_domain="Bayesian reasoning",
        prior_experience="novice",
        preferred_session_minutes=20,
        motivation_notes="Curious and wants quick visible progress.",
    )
    run_state = build_initial_run_state(profile)
    plan = build_first_session_plan(profile, concepts)
    learner_state = LearnerState(learner_id=profile.learner_id)

    learner_state = apply_demo_evidence(learner_state, "bayes-prior", "2026-03-13T12:00:00+00:00")

    stop = StopCriteria(
        min_mastered_concepts=1,
        min_average_score=0.70,
        min_average_confidence=0.20,
        required_capstones=[],
    )
    result = run_learning_cycle(learner_state, run_state, concepts, stop)

    payload = {
        "first_session_plan": plan.model_dump(),
        "cycle_result": result,
        "records": [r.model_dump() for r in learner_state.records],
    }
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
