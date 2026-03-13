from pathlib import Path
from didactopus.course_ingest import parse_source_file, merge_source_records, extract_concept_candidates
from didactopus.rule_policy import RuleContext, build_default_rules, run_rules
from didactopus.pack_emitter import build_draft_pack, write_draft_pack


def test_emit_multisource_pack(tmp_path: Path) -> None:
    src = tmp_path / "course.md"
    src.write_text("# C\n\n## M1\n### Lesson A\n- Objective: Explain Topic A.\n- Exercise: Do task A.\nTopic A body.", encoding="utf-8")
    course = merge_source_records([parse_source_file(src, title="Course")], course_title="Course")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())
    draft = build_draft_pack(course, ctx.concepts, "Tester", "REVIEW", ctx.review_flags, [])
    write_draft_pack(draft, tmp_path / "out")
    assert (tmp_path / "out" / "pack.yaml").exists()
    assert (tmp_path / "out" / "conflict_report.md").exists()
