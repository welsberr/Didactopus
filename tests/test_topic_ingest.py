import json
from pathlib import Path
from didactopus.document_adapters import adapt_document
from didactopus.document_adapters import adapt_documents
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


def test_document_to_course_skips_empty_sections(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    a.write_text("# T\n\n## Empty\n\n### Filled\nBody.", encoding="utf-8")
    doc = adapt_document(a)
    course = document_to_course(doc, "Topic")
    assert [lesson.title for lesson in course.modules[0].lessons] == ["Filled"]


def test_document_to_course_parses_bulleted_objectives_and_exercises(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    a.write_text(
        "# T\n\n## M\n### Shannon Entropy\n- Objective: Explain uncertainty.\n- Exercise: Compute entropy.\nBody.",
        encoding="utf-8",
    )
    doc = adapt_document(a)
    course = document_to_course(doc, "Topic")
    lesson = course.modules[0].lessons[0]
    assert lesson.objectives == ["Explain uncertainty."]
    assert lesson.exercises == ["Compute entropy."]


def test_extract_concepts_retains_lessons_but_filters_generic_terms(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    a.write_text(
        "# T\n\n## M\n### MIT OCW 6.050J Information and Entropy: Syllabus\n- Objective: Explain the course.\nBody.\n\n### Channel Capacity\n- Objective: Explain noisy channels.\n- Exercise: State a capacity limit.\nChannel Capacity links reliable communication to noise and coding.",
        encoding="utf-8",
    )
    doc = adapt_document(a)
    course = document_to_course(doc, "Topic")
    concepts = extract_concept_candidates(course)
    titles = {concept.title for concept in concepts}
    assert "MIT OCW 6.050J Information and Entropy: Syllabus" in titles
    assert "Explain" not in titles
    assert "Channel Capacity" in titles


def test_adapt_documents_from_doclift_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    doc_dir = bundle / "documents" / "lesson-a"
    doc_dir.mkdir(parents=True)
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "title": "Lecture 1. Example",
                        "document_kind": "lecture",
                        "output_dir": str(doc_dir),
                        "layout_path": str(doc_dir / "document.layout.json"),
                        "tables_path": str(doc_dir / "document.tables.json"),
                        "figures_path": str(doc_dir / "document.figures.json"),
                        "table_count": 1,
                        "figure_reference_count": 0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (doc_dir / "document.md").write_text("# Lecture 1. Example\n\n## Module\n### Lesson A\nBody.", encoding="utf-8")
    (doc_dir / "document.layout.json").write_text("[]", encoding="utf-8")
    (doc_dir / "document.tables.json").write_text(json.dumps({"source_path": "/tmp/source.doc", "tables": []}), encoding="utf-8")
    (doc_dir / "document.figures.json").write_text(json.dumps({"source_path": "/tmp/source.doc", "figure_references": []}), encoding="utf-8")

    docs = adapt_documents(bundle)

    assert len(docs) == 1
    assert docs[0].source_type == "doclift_bundle"
    assert docs[0].title == "Lecture 1. Example"
    assert docs[0].metadata["document_kind"] == "lecture"
    assert docs[0].metadata["doclift_bundle"] is True
    assert docs[0].source_path == "/tmp/source.doc"
