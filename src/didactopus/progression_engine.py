from __future__ import annotations
from datetime import datetime
import warnings

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
            evidence_coverage=0.0,
            evidence_count=0,
            last_updated=event.timestamp,
        )
        state.records.append(rec)

    weight = max(0.05, min(1.0, event.confidence_hint))
    rec.score = ((rec.score * rec.evidence_count) + (event.score * weight)) / max(1, rec.evidence_count + 1)
    rec.evidence_coverage = min(
        1.0,
        max(0.0, rec.evidence_coverage * (1.0 - decay) + reinforcement * weight + 0.10 * max(0.0, min(1.0, event.score))),
    )
    rec.evidence_count += 1
    rec.last_updated = event.timestamp
    state.history.append(event)
    return state


def decay_evidence_coverage(state: LearnerState, now_timestamp: str, daily_decay: float = 0.01) -> LearnerState:
    now = datetime.fromisoformat(now_timestamp)
    for record in state.records:
        if not record.last_updated:
            continue
        updated = datetime.fromisoformat(record.last_updated)
        elapsed_days = max(0.0, (now - updated).total_seconds() / 86400.0)
        record.evidence_coverage = max(0.0, record.evidence_coverage * ((1.0 - daily_decay) ** elapsed_days))
    return state


def decay_confidence(state: LearnerState, now_timestamp: str, daily_decay: float = 0.01) -> LearnerState:
    warnings.warn(
        "decay_confidence() is deprecated; use decay_evidence_coverage().",
        DeprecationWarning,
        stacklevel=2,
    )
    return decay_evidence_coverage(state, now_timestamp, daily_decay)
