from pathlib import Path
from didactopus.document_adapters import adapt_document
from didactopus.topic_ingest import document_to_course, build_topic_bundle, merge_courses_into_topic_course, extract_concept_candidates


def test_cross_course_merge(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.docx"
    a.write_text("# T\n\n## M\n### L1\nBody A", encoding="utf-8")
    b.write_text("# T\n\n## M\n### L1\nBody B", encoding="utf-8")

    docs = [adapt_document(a), adapt_document(b)]
    courses = [document_to_course(doc, "Topic") for doc in docs]
    topic = build_topic_bundle("Topic", courses)
    merged = merge_courses_into_topic_course(topic)
    assert len(merged.modules) >= 1
    assert len(merged.modules[0].lessons) == 1


def test_extract_concepts(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    a.write_text("# T\n\n## M\n### Lesson A\nObjective: Explain Topic A.\nBody.", encoding="utf-8")
    doc = adapt_document(a)
    course = document_to_course(doc, "Topic")
    concepts = extract_concept_candidates(course)
    assert len(concepts) >= 1
