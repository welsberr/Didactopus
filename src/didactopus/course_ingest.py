from __future__ import annotations

import re
from .course_schema import NormalizedCourse, Module, Lesson, ConceptCandidate

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def extract_key_terms(text: str, min_term_length: int = 4, max_terms: int = 8) -> list[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9\-]{%d,}\b" % (min_term_length - 1), text)
    seen = set()
    ordered = []
    for term in candidates:
        if term not in seen:
            seen.add(term)
            ordered.append(term)
        if len(ordered) >= max_terms:
            break
    return ordered


def parse_markdown_course(text: str, title: str, source_name: str = "", source_url: str = "", rights_note: str = "") -> NormalizedCourse:
    lines = text.splitlines()
    modules: list[Module] = []
    current_module: Module | None = None
    current_lesson: Lesson | None = None
    body_buffer: list[str] = []

    def flush_body():
        nonlocal body_buffer, current_lesson
        if current_lesson is not None and body_buffer:
            current_lesson.body = "\n".join(body_buffer).strip()
            body_buffer = []

    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            heading = m.group(2).strip()
            if level == 1:
                continue
            elif level == 2:
                flush_body()
                if current_lesson is not None and current_module is not None:
                    current_module.lessons.append(current_lesson)
                    current_lesson = None
                if current_module is not None:
                    modules.append(current_module)
                current_module = Module(title=heading, lessons=[])
            elif level == 3:
                flush_body()
                if current_lesson is not None and current_module is not None:
                    current_module.lessons.append(current_lesson)
                current_lesson = Lesson(title=heading)
            continue

        bullet = BULLET_RE.match(line)
        if bullet and current_lesson is not None:
            item = bullet.group(1).strip()
            lower = item.lower()
            if lower.startswith("objective:"):
                current_lesson.objectives.append(item.split(":", 1)[1].strip())
            elif lower.startswith("exercise:"):
                current_lesson.exercises.append(item.split(":", 1)[1].strip())
            else:
                body_buffer.append(line)
        else:
            body_buffer.append(line)

    flush_body()
    if current_lesson is not None and current_module is not None:
        current_module.lessons.append(current_lesson)
    if current_module is not None:
        modules.append(current_module)

    course = NormalizedCourse(
        title=title,
        source_name=source_name,
        source_url=source_url,
        rights_note=rights_note,
        modules=modules,
    )
    for module in course.modules:
        for lesson in module.lessons:
            lesson.key_terms = extract_key_terms(f"{lesson.title}\n{lesson.body}")
    return course


def extract_concept_candidates(course: NormalizedCourse) -> list[ConceptCandidate]:
    concepts: list[ConceptCandidate] = []
    seen_ids: set[str] = set()
    for module in course.modules:
        for lesson in module.lessons:
            title_id = slugify(lesson.title)
            if title_id not in seen_ids:
                seen_ids.add(title_id)
                concepts.append(
                    ConceptCandidate(
                        id=title_id,
                        title=lesson.title,
                        description=lesson.body[:240].strip(),
                        source_modules=[module.title],
                        source_lessons=[lesson.title],
                        mastery_signals=list(lesson.objectives[:3] or lesson.exercises[:2]),
                    )
                )
            for term in lesson.key_terms:
                term_id = slugify(term)
                if term_id in seen_ids:
                    continue
                seen_ids.add(term_id)
                concepts.append(
                    ConceptCandidate(
                        id=term_id,
                        title=term,
                        description=f"Candidate concept extracted from lesson '{lesson.title}'.",
                        source_modules=[module.title],
                        source_lessons=[lesson.title],
                        mastery_signals=list(lesson.objectives[:2]),
                    )
                )
    return concepts
