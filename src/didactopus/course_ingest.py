from __future__ import annotations

import re
from pathlib import Path
from .course_schema import NormalizedCourse, NormalizedSourceRecord, Module, Lesson, ConceptCandidate

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def detect_source_type(path: str | Path) -> str:
    p = Path(path)
    name = p.name.lower()
    suffix = p.suffix.lower()
    if name.endswith(".transcript.txt"):
        return "transcript"
    if name.endswith(".syllabus.txt"):
        return "syllabus"
    if suffix in {".md"}:
        return "markdown"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".txt"}:
        return "text"
    return "unknown"


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
    if any(token in title_blob for token in ("foundation", "background", "course identity", "course description", "reading base", "learning norms")):
        return "overview"
    if any(token in title_blob for token in ("coding", "capacity", "compression", "error-correcting", "error correcting", "mutual information", "reversible", "quantum", "cryptography", "noise")):
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


def parse_markdown_like(text: str, title: str, source_name: str, source_path: str) -> NormalizedSourceRecord:
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
                current_lesson = Lesson(title=heading, source_refs=[source_name])
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

    for module in modules:
        for lesson in module.lessons:
            lesson.key_terms = extract_key_terms(f"{lesson.title}\n{lesson.body}")
    return NormalizedSourceRecord(
        source_name=source_name,
        source_type=detect_source_type(source_path),
        source_path=str(source_path),
        title=title,
        modules=modules,
    )


def parse_source_file(path: str | Path, title: str = "") -> NormalizedSourceRecord:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    inferred_title = title or p.stem.replace("_", " ").replace("-", " ").title()
    return parse_markdown_like(text=text, title=inferred_title, source_name=p.name, source_path=str(p))


def parse_markdown_course(text: str, course_title: str, rights_note: str = "") -> NormalizedCourse:
    record = parse_markdown_like(
        text=text,
        title=course_title,
        source_name=f"{slugify(course_title)}.md",
        source_path=f"{slugify(course_title)}.md",
    )
    return merge_source_records([record], course_title=course_title, rights_note=rights_note)


def merge_source_records(records: list[NormalizedSourceRecord], course_title: str, rights_note: str = "", merge_same_named_lessons: bool = True) -> NormalizedCourse:
    modules_by_title: dict[str, Module] = {}
    for record in records:
        for module in record.modules:
            target_module = modules_by_title.setdefault(module.title, Module(title=module.title, lessons=[]))
            if merge_same_named_lessons:
                lesson_map = {lesson.title: lesson for lesson in target_module.lessons}
                for lesson in module.lessons:
                    if lesson.title in lesson_map:
                        existing = lesson_map[lesson.title]
                        if lesson.body and lesson.body not in existing.body:
                            existing.body = (existing.body + "\n\n" + lesson.body).strip()
                        for item in lesson.objectives:
                            if item not in existing.objectives:
                                existing.objectives.append(item)
                        for item in lesson.exercises:
                            if item not in existing.exercises:
                                existing.exercises.append(item)
                        for item in lesson.key_terms:
                            if item not in existing.key_terms:
                                existing.key_terms.append(item)
                        for item in lesson.source_refs:
                            if item not in existing.source_refs:
                                existing.source_refs.append(item)
                    else:
                        target_module.lessons.append(lesson)
            else:
                target_module.lessons.extend(module.lessons)
    return NormalizedCourse(
        title=course_title,
        rights_note=rights_note,
        modules=list(modules_by_title.values()),
        source_records=records,
    )


def extract_concept_candidates(course: NormalizedCourse) -> list[ConceptCandidate]:
    concepts: list[ConceptCandidate] = []
    seen_ids: set[str] = set()
    for module in course.modules:
        for lesson in module.lessons:
            enrichment = _concept_enrichment(module, lesson)
            title_id = slugify(lesson.title)
            if title_id not in seen_ids:
                seen_ids.add(title_id)
                concepts.append(
                    ConceptCandidate(
                        id=title_id,
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
