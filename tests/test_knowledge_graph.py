from pathlib import Path
import json

from didactopus.course_ingest import parse_markdown_course, extract_concept_candidates
from didactopus.knowledge_graph import build_knowledge_graph, write_knowledge_graph
from didactopus.rule_policy import RuleContext, build_default_rules, run_rules


SAMPLE = """
# Sample Course

## Module 1
### Lesson A
- Objective: Explain Topic A.
- Exercise: Do task A.
Topic A body.

### Lesson B
- Objective: Explain Topic B.
Lesson B body.
"""


def test_build_knowledge_graph_contains_typed_nodes_and_edges(tmp_path: Path) -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())

    payload = build_knowledge_graph(course, ctx.concepts)
    node_types = {node["type"] for node in payload["nodes"]}
    edge_types = {edge["type"] for edge in payload["edges"]}

    assert payload["summary"]["concept_count"] >= 2
    assert "source" in node_types
    assert "lesson" in node_types
    assert "concept" in node_types
    assert "assessment_signal" in node_types
    assert "contains_lesson" in edge_types
    assert "teaches_concept" in edge_types or "supports_concept" in edge_types

    write_knowledge_graph(course, ctx.concepts, tmp_path)
    written = json.loads((tmp_path / "knowledge_graph.json").read_text(encoding="utf-8"))
    assert written["summary"]["node_count"] >= len(payload["nodes"])
