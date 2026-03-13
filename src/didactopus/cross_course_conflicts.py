from __future__ import annotations

from collections import defaultdict
from .course_schema import NormalizedCourse, ConceptCandidate


def detect_title_overlaps(course: NormalizedCourse) -> list[str]:
    lesson_to_sources = defaultdict(set)
    for module in course.modules:
        for lesson in module.lessons:
            for src in lesson.source_refs:
                lesson_to_sources[lesson.title.lower()].add(src)
    flags = []
    for title, sources in lesson_to_sources.items():
        if len(sources) > 1:
            flags.append(f"Lesson title '{title}' appears across multiple sources: {', '.join(sorted(sources))}")
    return flags


def detect_term_conflicts(course: NormalizedCourse) -> list[str]:
    term_to_lessons = defaultdict(set)
    for module in course.modules:
        for lesson in module.lessons:
            for term in lesson.key_terms:
                term_to_lessons[term.lower()].add(lesson.title)
    flags = []
    for term, lessons in term_to_lessons.items():
        if len(lessons) > 1:
            flags.append(f"Key term '{term}' appears in multiple lesson contexts: {', '.join(sorted(lessons))}")
    return flags


def detect_order_conflicts(course: NormalizedCourse) -> list[str]:
    # Placeholder heuristic: if same lesson title appears in multiple source_refs, flag for order review.
    flags = []
    for module in course.modules:
        for lesson in module.lessons:
            if len(set(lesson.source_refs)) > 1:
                flags.append(f"Lesson '{lesson.title}' was merged from multiple sources; review ordering assumptions.")
    return flags


def detect_thin_concepts(concepts: list[ConceptCandidate]) -> list[str]:
    flags = []
    for concept in concepts:
        if len(concept.description.strip()) < 20:
            flags.append(f"Concept '{concept.title}' has a very thin description.")
        if not concept.mastery_signals:
            flags.append(f"Concept '{concept.title}' has no extracted mastery signals.")
    return flags
