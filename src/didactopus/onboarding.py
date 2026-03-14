from __future__ import annotations
from .orchestration_models import LearnerProfile, SessionPlan, RunState

def build_initial_run_state(profile: LearnerProfile) -> RunState:
    return RunState(profile=profile, status="onboarding")

def build_first_session_plan(profile: LearnerProfile, concepts: list[dict]) -> SessionPlan:
    first_title = concepts[0].get("title", "Foundations") if concepts else "Foundations"
    return SessionPlan(
        headline=f"Start with {first_title}",
        next_action=f"Read the short orientation, then attempt one guided exercise on {first_title}.",
        why_now="Early success lowers activation energy and gives the learner a clear entry point.",
        estimated_minutes=min(max(profile.preferred_session_minutes, 15), 35),
        tasks=[
            "Read the one-screen topic orientation",
            f"Try one guided exercise on {first_title}",
            "Write a short explanation in your own words",
        ],
        reward_note="You should finish this session with a visible first mastery marker.",
    )
