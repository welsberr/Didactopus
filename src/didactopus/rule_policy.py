from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from .course_schema import NormalizedCourse, ConceptCandidate


@dataclass
class RuleContext:
    course: NormalizedCourse
    concepts: list[ConceptCandidate]
    review_flags: list[str] = field(default_factory=list)


@dataclass
class Rule:
    name: str
    predicate: Callable[[RuleContext], bool]
    action: Callable[[RuleContext], None]


def order_based_prerequisite_rule(context: RuleContext) -> None:
    concept_titles = {c.title: c for c in context.concepts}
    previous = None
    for module in context.course.modules:
        for lesson in module.lessons:
            current = concept_titles.get(lesson.title)
            if current is not None and previous is not None and previous.id not in current.prerequisites:
                current.prerequisites.append(previous.id)
            if current is not None:
                previous = current


def duplicate_term_merge_rule(context: RuleContext) -> None:
    seen = {}
    deduped = []
    for concept in context.concepts:
        key = concept.title.strip().lower()
        if key in seen:
            seen[key].source_modules.extend(x for x in concept.source_modules if x not in seen[key].source_modules)
            seen[key].source_lessons.extend(x for x in concept.source_lessons if x not in seen[key].source_lessons)
            seen[key].source_courses.extend(x for x in concept.source_courses if x not in seen[key].source_courses)
            if concept.description and len(seen[key].description) < len(concept.description):
                seen[key].description = concept.description
        else:
            seen[key] = concept
            deduped.append(concept)
    context.concepts[:] = deduped


def project_detection_rule(context: RuleContext) -> None:
    for module in context.course.modules:
        joined = " ".join(lesson.body for lesson in module.lessons).lower()
        if "project" in joined or "capstone" in joined:
            context.review_flags.append(f"Module '{module.title}' appears to contain project-like material; review project extraction.")


def review_flag_rule(context: RuleContext) -> None:
    for module in context.course.modules:
        if not any(lesson.exercises for lesson in module.lessons):
            context.review_flags.append(f"Module '{module.title}' has no explicit exercises; mastery signals may be weak.")
    for concept in context.concepts:
        if not concept.mastery_signals:
            context.review_flags.append(f"Concept '{concept.title}' has no extracted mastery signals; review manually.")


def build_default_rules(enable_prereq=True, enable_merge=True, enable_projects=True, enable_review=True) -> list[Rule]:
    rules = []
    if enable_prereq:
        rules.append(Rule("order_based_prerequisite_rule", lambda ctx: True, order_based_prerequisite_rule))
    if enable_merge:
        rules.append(Rule("duplicate_term_merge_rule", lambda ctx: True, duplicate_term_merge_rule))
    if enable_projects:
        rules.append(Rule("project_detection_rule", lambda ctx: True, project_detection_rule))
    if enable_review:
        rules.append(Rule("review_flag_rule", lambda ctx: True, review_flag_rule))
    return rules


def run_rules(context: RuleContext, rules: list[Rule]) -> RuleContext:
    for rule in rules:
        if rule.predicate(context):
            rule.action(context)
    return context
