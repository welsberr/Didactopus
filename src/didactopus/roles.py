from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DidactopusRole:
    role_id: str
    display_name: str
    purpose: str
    default_model_alias: str
    pending_notice: str


DIDACTOPUS_ROLES: tuple[DidactopusRole, ...] = (
    DidactopusRole(
        role_id="mentor",
        display_name="Mentor",
        purpose="Guide the learner with sequencing, hints, and conceptual framing.",
        default_model_alias="planner",
        pending_notice="Didactopus is reviewing the next learning step before answering.",
    ),
    DidactopusRole(
        role_id="learner",
        display_name="Learner",
        purpose="Simulate or support the learner-side voice during transcript and study demos.",
        default_model_alias="writer",
        pending_notice="Didactopus is drafting the learner-side reflection now.",
    ),
    DidactopusRole(
        role_id="practice",
        display_name="Practice Designer",
        purpose="Create reasoning-heavy exercises and checks without giving away full solutions.",
        default_model_alias="writer",
        pending_notice="Didactopus is designing a practice task for you now.",
    ),
    DidactopusRole(
        role_id="project_advisor",
        display_name="Project Advisor",
        purpose="Suggest capstones and synthesis work that require independent execution.",
        default_model_alias="planner",
        pending_notice="Didactopus is sketching a project direction now.",
    ),
    DidactopusRole(
        role_id="evaluator",
        display_name="Evaluator",
        purpose="Critique learner work, identify weaknesses, and assess evidence of mastery.",
        default_model_alias="reviewer",
        pending_notice="Didactopus is evaluating the work before replying.",
    ),
)

ROLE_INDEX = {role.role_id: role for role in DIDACTOPUS_ROLES}


def default_role_to_model() -> dict[str, str]:
    return {role.role_id: role.default_model_alias for role in DIDACTOPUS_ROLES}


def role_ids() -> list[str]:
    return [role.role_id for role in DIDACTOPUS_ROLES]


def get_role(role_id: str) -> DidactopusRole | None:
    return ROLE_INDEX.get(role_id)
