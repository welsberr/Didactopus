from pathlib import Path
from didactopus.course_ingest import parse_source_file, merge_source_records, extract_concept_candidates


def test_merge_source_records(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.transcript.txt"
    a.write_text("# C\n\n## M1\n### L1\n- Objective: Explain A.\nText A.", encoding="utf-8")
    b.write_text("# C\n\n## M1\n### L1\nExtra transcript detail.", encoding="utf-8")

    records = [parse_source_file(a, title="Course"), parse_source_file(b, title="Course")]
    course = merge_source_records(records, course_title="Course")
    assert len(course.modules) == 1
    assert len(course.modules[0].lessons) == 1
    assert len(course.modules[0].lessons[0].source_refs) >= 1


def test_extract_candidates_from_merged(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    a.write_text("# C\n\n## M1\n### Lesson A\n- Objective: Explain Topic A.\nBody.", encoding="utf-8")
    course = merge_source_records([parse_source_file(a, title="Course")], course_title="Course")
    concepts = extract_concept_candidates(course)
    assert len(concepts) >= 1
