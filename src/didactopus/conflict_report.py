from __future__ import annotations

from collections import defaultdict
from .course_schema import NormalizedCourse, ConceptCandidate


def detect_duplicate_lessons(course: NormalizedCourse) -> list[str]:
    seen: dict[str, list[str]] = defaultdict(list)
    for module in course.modules:
        for lesson in module.lessons:
            seen[lesson.title.lower()].append(module.title)
    flags = []
    for title, modules in seen.items():
        if len(modules) > 1:
            flags.append(f"Lesson title '{title}' appears in multiple modules: {', '.join(sorted(set(modules)))}")
    return flags


def detect_term_conflicts(course: NormalizedCourse) -> list[str]:
    contexts: dict[str, set[str]] = defaultdict(set)
    for module in course.modules:
        for lesson in module.lessons:
            for term in lesson.key_terms:
                contexts[term.lower()].add(lesson.title)
    flags = []
    for term, lessons in contexts.items():
        if len(lessons) > 1:
            flags.append(f"Key term '{term}' appears in multiple lesson contexts: {', '.join(sorted(lessons))}")
    return flags


def detect_thin_concepts(concepts: list[ConceptCandidate]) -> list[str]:
    flags = []
    for concept in concepts:
        if not concept.mastery_signals:
            flags.append(f"Concept '{concept.title}' has no mastery signals.")
        if len(concept.description.strip()) < 20:
            flags.append(f"Concept '{concept.title}' has a very thin description.")
    return flags
