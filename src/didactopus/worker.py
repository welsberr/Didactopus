from __future__ import annotations
from .repository import get_evaluator_job, update_evaluator_job, load_learner_state, save_learner_state
from .engine import apply_evidence
from .models import EvidenceEvent
import time

def process_job(job_id: int):
    job = get_evaluator_job(job_id)
    if job is None:
        return
    score = 0.78 if len(job.submitted_text.strip()) > 20 else 0.62
    confidence_hint = 0.72 if len(job.submitted_text.strip()) > 20 else 0.45
    notes = "Prototype evaluator: longer responses scored somewhat higher."
    update_evaluator_job(job_id, "completed", score=score, confidence_hint=confidence_hint, notes=notes, trace={"notes": ["completed"]})
    state = load_learner_state(job.learner_id)
    state = apply_evidence(state, EvidenceEvent(concept_id=job.concept_id, dimension="mastery", score=score, confidence_hint=confidence_hint, timestamp="2026-03-13T12:00:00+00:00", kind="review", source_id=f"evaluator-job-{job_id}"))
    save_learner_state(state)

def main():
    while True:
        time.sleep(60)
