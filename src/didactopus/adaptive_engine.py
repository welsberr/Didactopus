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
    status: dict[str, NodeStatus] = {}
    for concept_key in nx.topological_sort(merged.graph):
        if concept_key in profile.mastered_concepts:
            status[concept_key] = "hidden" if profile.hide_mastered else "mastered"
            continue
        prereqs = set(merged.graph.predecessors(concept_key))
        if prereqs.issubset(profile.mastered_concepts):
            status[concept_key] = "ready"
        else:
            status[concept_key] = "blocked"
    return status


def select_next_best_concepts(status: dict[str, NodeStatus], limit: int = 5) -> list[str]:
    return [concept for concept, s in status.items() if s == "ready"][:limit]


def recommend_projects(merged: MergedLearningGraph, profile: LearnerProfile) -> list[dict]:
    eligible = []
    for project in merged.project_catalog:
        if set(project["prerequisites"]).issubset(profile.mastered_concepts):
            eligible.append(project)
    return eligible


def build_adaptive_plan(merged: MergedLearningGraph, profile: LearnerProfile, next_limit: int = 5) -> AdaptivePlan:
    status = classify_node_status(merged, profile)
    roadmap = []
    for concept_key in nx.topological_sort(merged.graph):
        node_state = status[concept_key]
        if node_state == "hidden":
            continue
        concept = merged.concept_data[concept_key]
        roadmap.append({
            "concept_key": concept_key,
            "title": concept["title"],
            "pack": concept["pack"],
            "status": node_state,
            "prerequisites": list(merged.graph.predecessors(concept_key)),
        })

    return AdaptivePlan(
        node_status=status,
        learner_roadmap=roadmap,
        next_best_concepts=select_next_best_concepts(status, limit=next_limit),
        eligible_projects=recommend_projects(merged, profile),
    )
