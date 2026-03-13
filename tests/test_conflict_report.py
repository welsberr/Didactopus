from pathlib import Path
from didactopus.course_ingest import parse_source_file, merge_source_records, extract_concept_candidates
from didactopus.conflict_report import detect_duplicate_lessons, detect_term_conflicts, detect_thin_concepts


def test_conflict_detection(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("# C\n\n## M1\n### Bayesian Updating\nPrior and Posterior are discussed here.", encoding="utf-8")
    b.write_text("# C\n\n## M2\n### Bayesian Updating\nPrior and Posterior appear again.", encoding="utf-8")
    course = merge_source_records([parse_source_file(a, title="Course"), parse_source_file(b, title="Course")], course_title="Course", merge_same_named_lessons=False)
    concepts = extract_concept_candidates(course)
    assert isinstance(detect_duplicate_lessons(course), list)
    assert isinstance(detect_term_conflicts(course), list)
    assert isinstance(detect_thin_concepts(concepts), list)
