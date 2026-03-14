from __future__ import annotations
from datetime import datetime, timezone
from .learner_state import LearnerState, EvidenceEvent, MasteryRecord

def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

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

    prev_score = rec.score
    prev_conf = rec.confidence

    # weighted incremental update
    weight = max(0.05, min(1.0, event.confidence_hint))
    rec.score = ((prev_score * rec.evidence_count) + (event.score * weight)) / max(1, rec.evidence_count + 1)

    # confidence grows with repeated evidence and quality, but is bounded
    rec.confidence = min(
        1.0,
        max(
            0.0,
            prev_conf * (1.0 - decay) + reinforcement * weight + 0.10 * max(0.0, min(1.0, event.score))
        ),
    )

    rec.evidence_count += 1
    rec.last_updated = event.timestamp
    state.history.append(event)
    return state

def decay_confidence(state: LearnerState, now_ts: str, daily_decay: float = 0.0025) -> LearnerState:
    now = _parse_ts(now_ts)
    for rec in state.records:
        if not rec.last_updated:
            continue
        then = _parse_ts(rec.last_updated)
        delta_days = max(0.0, (now - then).total_seconds() / 86400.0)
        factor = max(0.0, 1.0 - daily_decay * delta_days)
        rec.confidence = max(0.0, rec.confidence * factor)
    return state
