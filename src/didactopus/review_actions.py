from __future__ import annotations
from .review_schema import ReviewAction, ReviewLedgerEntry, ReviewSession

def _find_concept(session: ReviewSession, concept_id: str):
    for concept in session.draft_pack.concepts:
        if concept.concept_id == concept_id:
            return concept
    return None

def apply_action(session: ReviewSession, reviewer: str, action: ReviewAction) -> None:
    target = _find_concept(session, action.target)
    if action.action_type == "set_status" and target is not None:
        target.status = action.payload.get("status", target.status)
    elif action.action_type == "edit_prerequisites" and target is not None:
        target.prerequisites = list(action.payload.get("prerequisites", target.prerequisites))
    elif action.action_type == "edit_title" and target is not None:
        target.title = action.payload.get("title", target.title)
    elif action.action_type == "edit_description" and target is not None:
        target.description = action.payload.get("description", target.description)
    elif action.action_type == "edit_notes" and target is not None:
        target.notes = list(action.payload.get("notes", target.notes))
    elif action.action_type == "resolve_conflict":
        conflict = action.payload.get("conflict", "")
        if conflict in session.draft_pack.conflicts:
            session.draft_pack.conflicts.remove(conflict)
    session.ledger.append(ReviewLedgerEntry(reviewer=reviewer, action=action))
