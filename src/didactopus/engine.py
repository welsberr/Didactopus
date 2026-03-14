from __future__ import annotations
from collections import defaultdict
from .models import LearnerState, PackData

def concept_depths(pack: PackData) -> dict[str, int]:
    concept_map = {c.id: c for c in pack.concepts}
    memo = {}
    def depth(cid: str) -> int:
        if cid in memo:
            return memo[cid]
        c = concept_map[cid]
        if not c.prerequisites:
            memo[cid] = 0
        else:
            memo[cid] = 1 + max(depth(pid) for pid in c.prerequisites if pid in concept_map)
        return memo[cid]
    for cid in concept_map:
        depth(cid)
    return memo

def stable_layout(pack: PackData, width: int = 900, height: int = 520):
    depths = concept_depths(pack)
    layers = defaultdict(list)
    for c in pack.concepts:
        layers[depths.get(c.id, 0)].append(c)
    positions = {}
    max_depth = max(layers.keys()) if layers else 0
    for d in sorted(layers):
        nodes = sorted(layers[d], key=lambda c: c.id)
        y = 90 + d * ((height - 160) / max(1, max_depth))
        for idx, node in enumerate(nodes):
            if node.position is not None:
                positions[node.id] = {"x": node.position.x, "y": node.position.y, "source": "pack_authored"}
            else:
                spacing = width / (len(nodes) + 1)
                x = spacing * (idx + 1)
                positions[node.id] = {"x": x, "y": y, "source": "auto_layered"}
    return positions

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
    layout = stable_layout(pack)
    scores = {c.id: 0.0 for c in pack.concepts}
    frames = []
    history = sorted(state.history, key=lambda x: x.timestamp)
    static_edges = [{"source": pre, "target": c.id, "kind": "prerequisite"} for c in pack.concepts for pre in c.prerequisites]
    static_cross = [{
        "source": c.id,
        "target_pack_id": link.target_pack_id,
        "target_concept_id": link.target_concept_id,
        "relationship": link.relationship,
        "kind": "cross_pack"
    } for c in pack.concepts for link in c.cross_pack_links]
    for idx, ev in enumerate(history):
        if ev.concept_id in scores:
            scores[ev.concept_id] = ev.score
        nodes = []
        for cid, concept in concepts.items():
            score = scores.get(cid, 0.0)
            status = concept_status(scores, concept)
            pos = layout[cid]
            nodes.append({
                "id": cid,
                "title": concept.title,
                "score": score,
                "status": status,
                "size": 20 + int(score * 30),
                "x": pos["x"],
                "y": pos["y"],
                "layout_source": pos["source"],
            })
        frames.append({
            "index": idx,
            "timestamp": ev.timestamp,
            "event_kind": ev.kind,
            "focus_concept_id": ev.concept_id,
            "nodes": nodes,
            "edges": static_edges,
            "cross_pack_links": static_cross,
        })
    if not frames:
        nodes = []
        for c in pack.concepts:
            pos = layout[c.id]
            nodes.append({
                "id": c.id,
                "title": c.title,
                "score": 0.0,
                "status": "available" if not c.prerequisites else "locked",
                "size": 20,
                "x": pos["x"],
                "y": pos["y"],
                "layout_source": pos["source"],
            })
        frames.append({"index": 0, "timestamp": "", "event_kind": "empty", "focus_concept_id": "", "nodes": nodes, "edges": static_edges, "cross_pack_links": static_cross})
    return frames
