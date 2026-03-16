from pathlib import Path
import json

from didactopus.course_ingest import parse_markdown_course
from didactopus.pack_emitter import build_source_corpus, write_source_corpus


SAMPLE = """
# Sample Course

## Module 1
### Lesson A
- Objective: Explain Topic A.
- Exercise: Solve Task A.
Topic A body.
"""


def test_build_source_corpus_preserves_lesson_text_and_signals(tmp_path: Path) -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    corpus = build_source_corpus(course)

    assert corpus["course_title"] == "Sample Course"
    assert corpus["sources"]
    assert any(fragment["kind"] == "lesson_body" and "Topic A body." in fragment["text"] for fragment in corpus["fragments"])
    assert any(fragment["kind"] == "objective" and "Explain Topic A." in fragment["text"] for fragment in corpus["fragments"])
    assert any(fragment["kind"] == "exercise" and "Solve Task A." in fragment["text"] for fragment in corpus["fragments"])

    write_source_corpus(course, tmp_path)
    written = json.loads((tmp_path / "source_corpus.json").read_text(encoding="utf-8"))
    assert written["fragments"]
