from didactopus.orchestration_models import LearnerProfile
from didactopus.onboarding import build_initial_run_state, build_first_session_plan

def test_first_session_plan_has_clear_next_action():
    profile = LearnerProfile(learner_id="u1", preferred_session_minutes=20)
    state = build_initial_run_state(profile)
    plan = build_first_session_plan(profile, [{"id": "c1", "title": "Foundations"}])
    assert state.status == "onboarding"
    assert "Foundations" in plan.headline
    assert len(plan.tasks) >= 1
