from __future__ import annotations
from .models import LearnerState, EvidenceEvent, MasteryRecord, PackData

def get_record(state: LearnerState, concept_id: str, dimension: str = "mastery") -> MasteryRecord | None:
    for rec in state.records:
        if rec.concept_id == concept_id and rec.dimension == dimension:
            return rec
    return None

def apply_evidence(
    state: LearnerState,
    event: EvidenceEvent,
    decay: float = 0.05,
    reinforcement: float = 0.25,
) -> LearnerState:
    rec = get_record(state, event.concept_id, event.dimension)
    if rec is None:
        rec = MasteryRecord(
            concept_id=event.concept_id,
            dimension=event.dimension,
            score=0.0,
            confidence=0.0,
            evidence_count=0,
            last_updated=event.timestamp,
        )
        state.records.append(rec)

    weight = max(0.05, min(1.0, event.confidence_hint))
    rec.score = ((rec.score * rec.evidence_count) + (event.score * weight)) / max(1, rec.evidence_count + 1)
    rec.confidence = min(
        1.0,
        max(0.0, rec.confidence * (1.0 - decay) + reinforcement * weight + 0.10 * max(0.0, min(1.0, event.score))),
    )
    rec.evidence_count += 1
    rec.last_updated = event.timestamp
    state.history.append(event)
    return state

def prereqs_satisfied(state: LearnerState, concept, min_score: float = 0.65, min_confidence: float = 0.45) -> bool:
    for pid in concept.prerequisites:
        rec = get_record(state, pid, concept.masteryDimension)
        if rec is None or rec.score < min_score or rec.confidence < min_confidence:
            return False
    return True

def concept_status(state: LearnerState, concept, min_score: float = 0.65, min_confidence: float = 0.45) -> str:
    rec = get_record(state, concept.id, concept.masteryDimension)
    if rec and rec.score >= min_score and rec.confidence >= min_confidence:
        return "mastered"
    if prereqs_satisfied(state, concept, min_score, min_confidence):
        return "active" if rec else "available"
    return "locked"

def recommend_next(state: LearnerState, pack: PackData) -> list[dict]:
    cards = []
    for concept in pack.concepts:
        status = concept_status(state, concept)
        rec = get_record(state, concept.id, concept.masteryDimension)
        if status in {"available", "active"}:
            cards.append({
                "id": concept.id,
                "title": f"Work on {concept.title}",
                "minutes": 15 if status == "available" else 10,
                "reason": (
                    "Prerequisites are satisfied, so this is the best next unlock."
                    if status == "available"
                    else "You have started this concept, but mastery is not yet secure."
                ),
                "why": [
                    "Prerequisite check passed",
                    f"Current score: {rec.score:.2f}" if rec else "No evidence recorded yet",
                    f"Current confidence: {rec.confidence:.2f}" if rec else "Confidence starts after your first exercise",
                ],
                "reward": concept.exerciseReward or f"{concept.title} progress recorded",
                "conceptId": concept.id,
                "scoreHint": 0.82 if status == "available" else 0.76,
                "confidenceHint": 0.72 if status == "available" else 0.55,
            })
    for rec in state.records:
        if rec.dimension == "mastery" and rec.confidence < 0.40:
            concept = next((c for c in pack.concepts if c.id == rec.concept_id), None)
            if concept:
                cards.append({
                    "id": f"{concept.id}-reinforce",
                    "title": f"Reinforce {concept.title}",
                    "minutes": 8,
                    "reason": "Your score is promising, but confidence is still thin.",
                    "why": [
                        f"Confidence {rec.confidence:.2f} is below reinforcement threshold",
                        "A small fresh exercise can stabilize recall",
                    ],
                    "reward": "Confidence ring grows",
                    "conceptId": concept.id,
                    "scoreHint": max(0.60, rec.score),
                    "confidenceHint": 0.30,
                })
    return cards[:4]
