from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
import networkx as nx

from .learning_graph import MergedLearningGraph

NodeStatus = Literal["mastered", "ready", "blocked", "hidden"]


@dataclass
class LearnerProfile:
    learner_id: str
    display_name: str = ""
    goals: list[str] = field(default_factory=list)
    mastered_concepts: set[str] = field(default_factory=set)
    hide_mastered: bool = True


@dataclass
class AdaptivePlan:
    node_status: dict[str, NodeStatus] = field(default_factory=dict)
    learner_roadmap: list[dict] = field(default_factory=list)
    next_best_concepts: list[str] = field(default_factory=list)
    eligible_projects: list[dict] = field(default_factory=list)


def classify_node_status(merged: MergedLearningGraph, profile: LearnerProfile) -> dict[str, NodeStatus]:
    status = {}
    for concept_key in nx.topological_sort(merged.graph):
        if concept_key in profile.mastered_concepts:
            status[concept_key] = "hidden" if profile.hide_mastered else "mastered"
            continue
        prereqs = set(merged.graph.predecessors(concept_key))
        status[concept_key] = "ready" if prereqs.issubset(profile.mastered_concepts) else "blocked"
    return status


def build_adaptive_plan(merged: MergedLearningGraph, profile: LearnerProfile, next_limit: int = 5) -> AdaptivePlan:
    status = classify_node_status(merged, profile)
    roadmap = []
    for concept_key in nx.topological_sort(merged.graph):
        state = status[concept_key]
        if state == "hidden":
            continue
        data = merged.concept_data[concept_key]
        roadmap.append({
            "concept_key": concept_key,
            "title": data["title"],
            "pack": data["pack"],
            "status": state,
            "prerequisites": list(merged.graph.predecessors(concept_key)),
        })

    eligible = [
        p for p in merged.project_catalog
        if set(p["prerequisites"]).issubset(profile.mastered_concepts)
    ]
    next_best = [k for k, s in status.items() if s == "ready"][:next_limit]
    return AdaptivePlan(status, roadmap, next_best, eligible)
