from pathlib import Path
import yaml
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


def test_emit_pack_can_write_groundrecall_query_bundle(tmp_path: Path) -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())
    groundrecall_bundle = {
        "bundle_kind": "groundrecall_query_bundle",
        "concept": {"concept_id": "concept::topic-a", "title": "Topic A"},
        "review_candidates": [{"candidate_id": "concept::topic-a", "rationale": "Topic A | lane=knowledge_capture | priority=20"}],
    }
    draft = build_draft_pack(
        course,
        ctx.concepts,
        "Tester",
        "REVIEW",
        ctx.review_flags,
        groundrecall_query_bundle=groundrecall_bundle,
    )
    write_draft_pack(draft, tmp_path)

    pack_yaml = (tmp_path / "pack.yaml").read_text(encoding="utf-8")
    bundle_payload = (tmp_path / "groundrecall_query_bundle.json").read_text(encoding="utf-8")
    notebook_payload = (tmp_path / "notebook_page.json").read_text(encoding="utf-8")
    assert "groundrecall_query_bundle.json" in pack_yaml
    assert "notebook_page.json" in pack_yaml
    assert '"bundle_kind": "groundrecall_query_bundle"' in bundle_payload
    assert '"page_kind": "didactopus_notebook_page"' in notebook_payload


def test_emit_pack_preserves_richer_concept_fields(tmp_path: Path) -> None:
    sample = """
# OCW Slice

## Broader Applications
### Thermodynamics and Entropy
- Objective: Explain how thermodynamic entropy relates to, and differs from, Shannon entropy.
- Exercise: Compare the two entropy notions and identify what is preserved across the analogy.
Entropy is a measure of uncertainty in the source model. The analogy is useful but dangerous when used loosely.
"""
    course = parse_markdown_course(sample, "OCW Slice")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())
    draft = build_draft_pack(course, ctx.concepts, "Tester", "REVIEW", ctx.review_flags)
    write_draft_pack(draft, tmp_path)

    concepts_yaml = yaml.safe_load((tmp_path / "concepts.yaml").read_text(encoding="utf-8"))
    concept = concepts_yaml["concepts"][0]
    assert concept["source_role"] == "nuance"
    assert concept["distinctions"]
    assert concept["definition_candidates"]
    assert concept["qualification_candidates"]
