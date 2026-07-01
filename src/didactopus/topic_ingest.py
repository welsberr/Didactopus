from __future__ import annotations

import re
from collections import defaultdict
from .course_schema import NormalizedDocument, NormalizedCourse, Module, Lesson, TopicBundle, ConceptCandidate
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

GENERIC_TERM_STOPWORDS = {
    "attribution",
    "build",
    "careful",
    "compare",
    "comparison",
    "compute",
    "course",
    "decide",
    "describe",
    "didactopus",
    "early",
    "exercise",
    "explain",
    "home",
    "identify",
    "independent",
    "later",
    "list",
    "notes",
    "objective",
    "open",
    "opencourseware",
    "produce",
    "programming",
    "reference",
    "source",
    "spring",
    "state",
    "structure",
    "summarize",
    "syllabus",
    "synthesis",
    "synthesize",
    "texts",
    "these",
    "ultimate",
    "unit",
    "work",
    "write",
}

def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def extract_key_terms(text: str, min_term_length: int = 4, max_terms: int = 8) -> list[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9\-]{%d,}\b" % (min_term_length - 1), text)
    seen = set()
    out = []
    for term in candidates:
        lower = term.lower()
        if lower in GENERIC_TERM_STOPWORDS:
            continue
        if term not in seen:
            seen.add(term)
            out.append(term)
        if len(out) >= max_terms:
            break
    return out


def _parse_signal_line(line: str) -> tuple[str | None, str]:
    stripped = line.strip()
    if stripped.startswith(("-", "*", "+")):
        stripped = stripped[1:].strip()
    lowered = stripped.lower()
    if lowered.startswith("objective:"):
        return "objective", stripped.split(":", 1)[1].strip()
    if lowered.startswith("exercise:"):
        return "exercise", stripped.split(":", 1)[1].strip()
    return None, stripped


def _lesson_sentences(lesson: Lesson) -> list[str]:
    parts = [lesson.body, *lesson.objectives, *lesson.exercises]
    joined = "\n".join(part.strip() for part in parts if part and part.strip())
    if not joined:
        return []
    sentences = []
    for chunk in SENTENCE_SPLIT_RE.split(joined):
        text = " ".join(chunk.split()).strip(" -")
        if text:
            sentences.append(text)
    return sentences


def _compact_description(lesson: Lesson, max_chars: int = 320) -> str:
    sentences = _lesson_sentences(lesson)
    if not sentences:
        return lesson.title
    out = []
    total = 0
    for sentence in sentences:
        candidate = sentence if sentence.endswith((".", "!", "?")) else f"{sentence}."
        if out and total + 1 + len(candidate) > max_chars:
            break
        out.append(candidate)
        total += len(candidate) + (1 if out[:-1] else 0)
        if len(out) >= 2:
            break
    return " ".join(out).strip()[:max_chars]


def _extract_sentences_by_patterns(sentences: list[str], patterns: list[str], max_items: int = 3) -> list[str]:
    compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    out: list[str] = []
    seen: set[str] = set()
    for sentence in sentences:
        lowered = sentence.lower()
        if lowered in seen:
            continue
        if any(pattern.search(sentence) for pattern in compiled):
            seen.add(lowered)
            out.append(sentence)
        if len(out) >= max_items:
            break
    return out


def _infer_source_role(module: Module, lesson: Lesson, distinctions: list[str], qualifications: list[str], constraints: list[str]) -> str:
    title_blob = " ".join([module.title, lesson.title, lesson.body]).lower()
    if distinctions or qualifications or constraints:
        return "nuance"
    if any(token in title_blob for token in ("foundation", "overview", "introduction", "background")):
        return "overview"
    if any(token in title_blob for token in ("method", "model", "test", "mechanism", "process", "coding", "capacity")):
        return "mechanism"
    return "overview"


def _concept_enrichment(module: Module, lesson: Lesson) -> dict[str, list[str] | str]:
    sentences = _lesson_sentences(lesson)
    distinctions = _extract_sentences_by_patterns(
        sentences,
        [
            r"\bcompare\b",
            r"\bcontrast\b",
            r"\bdistinguish\b",
            r"\bdiffer(?:ent|s)?\b",
            r"\brelat(?:e|es|ed)\b.+\band\b",
            r"\bnot\b.+\bbut\b",
            r"\bversus\b|\bvs\.?\b",
        ],
    )
    definitions = _extract_sentences_by_patterns(
        sentences,
        [
            r"\bis (?:a|an|the)\b",
            r"\bmeasure of\b",
            r"\brefers to\b",
            r"\bdefined as\b",
            r"\btreated as\b",
        ],
    )
    qualifications = _extract_sentences_by_patterns(
        sentences,
        [
            r"\bbut\b",
            r"\bhowever\b",
            r"\bwhile\b",
            r"\balthough\b",
            r"\bcareful\b",
            r"\bnot identical\b",
            r"\bdangerous\b",
        ],
    )
    constraints = _extract_sentences_by_patterns(
        sentences,
        [
            r"\bimpossible\b",
            r"\blimit(?:s)?\b",
            r"\bfailure mode(?:s)?\b",
            r"\bcannot\b",
            r"\bonly up to\b",
            r"\bin the long run\b",
            r"\babove capacity\b",
        ],
    )
    return {
        "source_role": _infer_source_role(module, lesson, distinctions, qualifications, constraints),
        "distinctions": distinctions,
        "definition_candidates": definitions,
        "qualification_candidates": qualifications,
        "constraint_candidates": constraints,
    }
def document_to_course(doc: NormalizedDocument, course_title: str) -> NormalizedCourse:
    # Conservative mapping: each section becomes a lesson; all lessons go into one module.
    lessons = []
    for section in doc.sections:
        body = section.body.strip()
        if not body:
            continue
        lines = body.splitlines()
        objectives = []
        exercises = []
        for line in lines:
            kind, value = _parse_signal_line(line)
            if kind == "objective":
                objectives.append(value)
            if kind == "exercise":
                exercises.append(value)
        lessons.append(
            Lesson(
                title=section.heading.strip() or "Untitled Lesson",
                body=body,
                objectives=objectives,
                exercises=exercises,
                key_terms=extract_key_terms(body),
                source_refs=[doc.source_path],
            )
        )
    module = Module(title=f"Imported from {doc.source_type.upper()}", lessons=lessons)
    return NormalizedCourse(title=course_title, modules=[module], source_records=[doc])


def build_topic_bundle(topic_title: str, courses: list[NormalizedCourse]) -> TopicBundle:
    return TopicBundle(topic_title=topic_title, courses=courses)


def merge_courses_into_topic_course(topic_bundle: TopicBundle, merge_same_named_lessons: bool = True) -> NormalizedCourse:
    modules_by_title: dict[str, Module] = {}
    source_records = []
    for course in topic_bundle.courses:
        source_records.extend(course.source_records)
        for module in course.modules:
            target_module = modules_by_title.setdefault(module.title, Module(title=module.title, lessons=[]))
            if merge_same_named_lessons:
                lesson_map = {lesson.title: lesson for lesson in target_module.lessons}
                for lesson in module.lessons:
                    if lesson.title in lesson_map:
                        existing = lesson_map[lesson.title]
                        if lesson.body and lesson.body not in existing.body:
                            existing.body = (existing.body + "\n\n" + lesson.body).strip()
                        for x in lesson.objectives:
                            if x not in existing.objectives:
                                existing.objectives.append(x)
                        for x in lesson.exercises:
                            if x not in existing.exercises:
                                existing.exercises.append(x)
                        for x in lesson.key_terms:
                            if x not in existing.key_terms:
                                existing.key_terms.append(x)
                        for x in lesson.source_refs:
                            if x not in existing.source_refs:
                                existing.source_refs.append(x)
                    else:
                        target_module.lessons.append(lesson)
            else:
                target_module.lessons.extend(module.lessons)
    return NormalizedCourse(title=topic_bundle.topic_title, modules=list(modules_by_title.values()), source_records=source_records)


def extract_concept_candidates(course: NormalizedCourse) -> list[ConceptCandidate]:
    concepts = []
    seen_ids = set()
    for module in course.modules:
        for lesson in module.lessons:
            enrichment = _concept_enrichment(module, lesson)
            cid = slugify(lesson.title)
            if cid not in seen_ids:
                seen_ids.add(cid)
                concepts.append(
                    ConceptCandidate(
                        id=cid,
                        title=lesson.title,
                        description=_compact_description(lesson),
                        source_modules=[module.title],
                        source_lessons=[lesson.title],
                        source_courses=list(lesson.source_refs),
                        mastery_signals=list(lesson.objectives[:3] or lesson.exercises[:2]),
                        source_role=str(enrichment["source_role"]),
                        distinctions=list(enrichment["distinctions"]),
                        definition_candidates=list(enrichment["definition_candidates"]),
                        qualification_candidates=list(enrichment["qualification_candidates"]),
                        constraint_candidates=list(enrichment["constraint_candidates"]),
                    )
                )
            for term in lesson.key_terms:
                tid = slugify(term)
                if tid in seen_ids:
                    continue
                if tid in {slugify(part) for part in lesson.title.split()}:
                    continue
                seen_ids.add(tid)
                concepts.append(
                    ConceptCandidate(
                        id=tid,
                        title=term,
                        description=f"Candidate concept extracted from lesson '{lesson.title}'.",
                        source_modules=[module.title],
                        source_lessons=[lesson.title],
                        source_courses=list(lesson.source_refs),
                        mastery_signals=list(lesson.objectives[:2]),
                        source_role=str(enrichment["source_role"]),
                        distinctions=list(enrichment["distinctions"][:1]),
                        definition_candidates=list(enrichment["definition_candidates"][:1]),
                        qualification_candidates=list(enrichment["qualification_candidates"][:1]),
                        constraint_candidates=list(enrichment["constraint_candidates"][:1]),
                    )
                )
    return concepts
