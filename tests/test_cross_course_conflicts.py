from pathlib import Path
from didactopus.document_adapters import adapt_document
from didactopus.topic_ingest import document_to_course, build_topic_bundle, merge_courses_into_topic_course, extract_concept_candidates
from didactopus.cross_course_conflicts import detect_title_overlaps, detect_term_conflicts, detect_order_conflicts, detect_thin_concepts


def test_conflict_detection(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("# T\n\n## M1\n### Bayesian Updating\nPrior and Posterior appear here.", encoding="utf-8")
    b.write_text("# T\n\n## M2\n### Bayesian Updating\nPrior and Posterior appear again.", encoding="utf-8")
    docs = [adapt_document(a), adapt_document(b)]
    courses = [document_to_course(doc, "Topic") for doc in docs]
    merged = merge_courses_into_topic_course(build_topic_bundle("Topic", courses), merge_same_named_lessons=False)
    concepts = extract_concept_candidates(merged)
    assert isinstance(detect_title_overlaps(merged), list)
    assert isinstance(detect_term_conflicts(merged), list)
    assert isinstance(detect_order_conflicts(merged), list)
    assert isinstance(detect_thin_concepts(concepts), list)
