"""Deterministic Didactopus adoption of ClaimWright decision challenges."""

from __future__ import annotations

from typing import Any


_STANDARD_ACTIONS = {
    "promote_mastery",
    "promote_source_support",
    "publish_pack",
    "change_instructional_policy",
}
_ESCALATED_ACTIONS = {"delete_learner_record", "export_private_learner_data"}
_ROUTINE_ACTIONS = {"mentor_turn", "practice_response", "reversible_hint", "learner_draft"}


def classify_decision_challenge(
    action: str,
    *,
    public_facing: bool = False,
    durable_memory_change: bool = False,
    destructive: bool = False,
    novel_path: bool = False,
) -> dict[str, Any]:
    """Return a bounded review classification without making a mastery decision."""

    action = action.strip()
    if not action:
        raise ValueError("action is required")
    triggers: list[str] = []
    if public_facing:
        triggers.append("public_release")
    if durable_memory_change:
        triggers.append("durable_memory_change")
    if destructive:
        triggers.append("destructive_action")
    if novel_path:
        triggers.append("novel_or_unfamiliar_path")

    if destructive or action in _ESCALATED_ACTIONS:
        level = "escalated"
    elif action in _STANDARD_ACTIONS or public_facing or durable_memory_change or novel_path:
        level = "standard"
    elif action in _ROUTINE_ACTIONS:
        level = "none"
    else:
        level = "quick"
    return {
        "schema_version": "didactopus.decision_challenge_classification.v1",
        "action": action,
        "review_level": level,
        "trigger_codes": sorted(set(triggers)),
        "challenge_required": level != "none",
        "authority": "classification only; learner mastery and publication authority remain separate.",
        "notes": [
            "Routine mentor, practice, and hint turns are not individually challenged.",
            "Learner evidence remains draft until the existing review/promotion workflow accepts it.",
        ],
    }
