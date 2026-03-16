from pathlib import Path
from didactopus.course_ingest import parse_markdown_course, extract_concept_candidates
from didactopus.knowledge_graph import write_knowledge_graph
from didactopus.rule_policy import RuleContext, build_default_rules, run_rules
from didactopus.pack_emitter import build_draft_pack, write_draft_pack, write_source_corpus

SAMPLE = '''
# Sample Course

## Module 1
### Lesson A
- Objective: Explain Topic A.
- Exercise: Do task A.
Topic A body.
'''

def test_emit_pack(tmp_path: Path) -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())
    draft = build_draft_pack(course, ctx.concepts, "Tester", "REVIEW", ctx.review_flags)
    write_draft_pack(draft, tmp_path)
    write_source_corpus(course, tmp_path)
    write_knowledge_graph(course, ctx.concepts, tmp_path)
    assert (tmp_path / "pack.yaml").exists()
    assert (tmp_path / "review_report.md").exists()
    assert (tmp_path / "source_corpus.json").exists()
    assert (tmp_path / "knowledge_graph.json").exists()
