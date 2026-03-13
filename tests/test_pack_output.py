from pathlib import Path
from didactopus.document_adapters import adapt_document
from didactopus.topic_ingest import document_to_course, build_topic_bundle, merge_courses_into_topic_course, extract_concept_candidates
from didactopus.rule_policy import RuleContext, build_default_rules, run_rules
from didactopus.pack_emitter import build_draft_pack, write_draft_pack


def test_emit_topic_pack(tmp_path: Path) -> None:
    src = tmp_path / "course.md"
    src.write_text("# T\n\n## M\n### L\nExercise: Do task A.\nTopic A body.", encoding="utf-8")
    doc = adapt_document(src)
    course = document_to_course(doc, "Topic")
    merged = merge_courses_into_topic_course(build_topic_bundle("Topic", [course]))
    concepts = extract_concept_candidates(merged)
    ctx = RuleContext(course=merged, concepts=concepts)
    run_rules(ctx, build_default_rules())
    draft = build_draft_pack(merged, ctx.concepts, "Tester", "REVIEW", ctx.review_flags, [])
    write_draft_pack(draft, tmp_path / "out")
    assert (tmp_path / "out" / "pack.yaml").exists()
    assert (tmp_path / "out" / "conflict_report.md").exists()
