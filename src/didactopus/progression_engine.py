from __future__ import annotations
from .learner_state import LearnerState, EvidenceEvent, MasteryRecord

def apply_evidence(
    state: LearnerState,
    event: EvidenceEvent,
    decay: float = 0.05,
    reinforcement: float = 0.25,
) -> LearnerState:
    rec = state.get_record(event.concept_id, event.dimension)
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
