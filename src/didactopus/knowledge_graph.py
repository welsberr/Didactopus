from __future__ import annotations

import json
import re
from pathlib import Path

from .course_schema import ConceptCandidate, NormalizedCourse


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def _source_node_id(source_path: str) -> str:
    return f"source::{_slugify(source_path)}"


def _module_node_id(module_title: str) -> str:
    return f"module::{_slugify(module_title)}"


def _lesson_node_id(module_title: str, lesson_title: str) -> str:
    return f"lesson::{_slugify(module_title)}::{_slugify(lesson_title)}"


def _concept_node_id(concept_id: str) -> str:
    return f"concept::{concept_id}"


def _signal_node_id(kind: str, lesson_title: str, idx: int) -> str:
    return f"{kind}::{_slugify(lesson_title)}::{idx}"


def _add_node(nodes: dict[str, dict], node_id: str, node_type: str, **attrs) -> None:
    node = nodes.setdefault(node_id, {"id": node_id, "type": node_type})
    for key, value in attrs.items():
        if value not in (None, "", [], {}):
            node[key] = value


def _add_edge(edges: list[dict], source: str, target: str, edge_type: str, justification: str, provenance: list[str] | None = None, confidence: float = 1.0) -> None:
    edges.append(
        {
            "source": source,
            "target": target,
            "type": edge_type,
            "justification": justification,
            "provenance": list(provenance or []),
            "confidence": confidence,
        }
    )


def build_knowledge_graph(course: NormalizedCourse, concepts: list[ConceptCandidate]) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    for source in course.source_records:
        source_id = _source_node_id(source.source_path)
        _add_node(
            nodes,
            source_id,
            "source",
            title=source.title or source.source_path,
            source_path=source.source_path,
            source_type=source.source_type,
            metadata=getattr(source, "metadata", {}),
        )

    concept_ids = {concept.id for concept in concepts}
    for concept in concepts:
        concept_node_id = _concept_node_id(concept.id)
        _add_node(
            nodes,
            concept_node_id,
            "concept",
            title=concept.title,
            description=concept.description,
            source_modules=list(concept.source_modules),
            source_lessons=list(concept.source_lessons),
            source_courses=list(concept.source_courses),
            mastery_signals=list(concept.mastery_signals),
        )

    for module in course.modules:
        module_id = _module_node_id(module.title)
        _add_node(nodes, module_id, "module", title=module.title)
        for lesson in module.lessons:
            lesson_id = _lesson_node_id(module.title, lesson.title)
            _add_node(
                nodes,
                lesson_id,
                "lesson",
                title=lesson.title,
                module_title=module.title,
                body=lesson.body,
                source_refs=list(lesson.source_refs),
                key_terms=list(lesson.key_terms),
            )
            _add_edge(
                edges,
                module_id,
                lesson_id,
                "contains_lesson",
                justification=f"Lesson '{lesson.title}' appears under module '{module.title}'.",
                provenance=list(lesson.source_refs),
            )
            for source_ref in lesson.source_refs:
                source_id = _source_node_id(source_ref)
                if source_id in nodes:
                    _add_edge(
                        edges,
                        source_id,
                        lesson_id,
                        "derived_lesson",
                        justification=f"Lesson '{lesson.title}' was ingested from source '{source_ref}'.",
                        provenance=[source_ref],
                    )

            for idx, objective in enumerate(lesson.objectives, start=1):
                objective_id = _signal_node_id("objective", lesson.title, idx)
                _add_node(nodes, objective_id, "assessment_signal", title=objective, signal_kind="objective")
                _add_edge(
                    edges,
                    lesson_id,
                    objective_id,
                    "has_objective",
                    justification=f"Objective {idx} was extracted from lesson '{lesson.title}'.",
                    provenance=list(lesson.source_refs),
                )

            for idx, exercise in enumerate(lesson.exercises, start=1):
                exercise_id = _signal_node_id("exercise", lesson.title, idx)
                _add_node(nodes, exercise_id, "assessment_signal", title=exercise, signal_kind="exercise")
                _add_edge(
                    edges,
                    lesson_id,
                    exercise_id,
                    "has_exercise",
                    justification=f"Exercise {idx} was extracted from lesson '{lesson.title}'.",
                    provenance=list(lesson.source_refs),
                )

            lesson_concept_id = _concept_node_id(_slugify(lesson.title))
            if lesson_concept_id in nodes:
                _add_edge(
                    edges,
                    lesson_id,
                    lesson_concept_id,
                    "teaches_concept",
                    justification=f"Lesson '{lesson.title}' yields the lesson-level concept '{lesson.title}'.",
                    provenance=list(lesson.source_refs),
                )

            for term in lesson.key_terms:
                term_id = _concept_node_id(_slugify(term))
                if term_id in nodes:
                    _add_edge(
                        edges,
                        lesson_id,
                        term_id,
                        "mentions_concept",
                        justification=f"Key term '{term}' was extracted from lesson '{lesson.title}'.",
                        provenance=list(lesson.source_refs),
                        confidence=0.7,
                    )

    for concept in concepts:
        concept_node_id = _concept_node_id(concept.id)
        for prereq in concept.prerequisites:
            prereq_id = _concept_node_id(prereq)
            if prereq_id in nodes:
                _add_edge(
                    edges,
                    prereq_id,
                    concept_node_id,
                    "prerequisite",
                    justification=f"Concept '{concept.title}' depends on prerequisite '{prereq}'.",
                    provenance=list(concept.source_courses),
                    confidence=0.85,
                )
        for lesson_title in concept.source_lessons:
            lesson_sources = [module.title for module in course.modules if any(lesson.title == lesson_title for lesson in module.lessons)]
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.title != lesson_title:
                        continue
                    lesson_id = _lesson_node_id(module.title, lesson.title)
                    if concept_node_id in nodes and lesson_id in nodes:
                        _add_edge(
                            edges,
                            lesson_id,
                            concept_node_id,
                            "supports_concept",
                            justification=f"Concept '{concept.title}' was extracted from lesson '{lesson.title}'.",
                            provenance=list(lesson.source_refs),
                            confidence=0.9 if concept.id == _slugify(lesson.title) else 0.7,
                        )

    return {
        "course_title": course.title,
        "rights_note": course.rights_note,
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "concept_count": len(concepts),
            "source_count": len(course.source_records),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def write_knowledge_graph(course: NormalizedCourse, concepts: list[ConceptCandidate], outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    payload = build_knowledge_graph(course, concepts)
    (out / "knowledge_graph.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
