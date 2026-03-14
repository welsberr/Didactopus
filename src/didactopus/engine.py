from __future__ import annotations
from .models import LearnerState, EvidenceEvent, MasteryRecord, PackData

def get_record(state: LearnerState, concept_id: str, dimension: str = "mastery") -> MasteryRecord | None:
    for rec in state.records:
        if rec.concept_id == concept_id and rec.dimension == dimension:
            return rec
    return None

def prereqs_satisfied(scores: dict[str, float], concept, min_score: float = 0.65) -> bool:
    for pid in concept.prerequisites:
        if scores.get(pid, 0.0) < min_score:
            return False
    return True

def concept_status(scores: dict[str, float], concept, min_score: float = 0.65) -> str:
    score = scores.get(concept.id, 0.0)
    if score >= min_score:
        return "mastered"
    if prereqs_satisfied(scores, concept, min_score):
        return "active" if score > 0 else "available"
    return "locked"

def build_graph_frames(state: LearnerState, pack: PackData):
    concepts = {c.id: c for c in pack.concepts}
    scores = {c.id: 0.0 for c in pack.concepts}
    frames = []
    history = sorted(state.history, key=lambda x: x.timestamp)
    for idx, ev in enumerate(history):
        if ev.concept_id in scores:
            scores[ev.concept_id] = ev.score
        nodes = []
        for cid, concept in concepts.items():
            score = scores.get(cid, 0.0)
            status = concept_status(scores, concept)
            nodes.append({
                "id": cid,
                "title": concept.title,
                "score": score,
                "status": status,
                "size": 20 + int(score * 30),
            })
        edges = []
        for cid, concept in concepts.items():
            for pre in concept.prerequisites:
                edges.append({"source": pre, "target": cid})
        frames.append({
            "index": idx,
            "timestamp": ev.timestamp,
            "event_kind": ev.kind,
            "focus_concept_id": ev.concept_id,
            "nodes": nodes,
            "edges": edges,
        })
    if not frames:
        nodes = [{"id": c.id, "title": c.title, "score": 0.0, "status": "available" if not c.prerequisites else "locked", "size": 20} for c in pack.concepts]
        edges = [{"source": pre, "target": c.id} for c in pack.concepts for pre in c.prerequisites]
        frames.append({"index": 0, "timestamp": "", "event_kind": "empty", "focus_concept_id": "", "nodes": nodes, "edges": edges})
    return frames
