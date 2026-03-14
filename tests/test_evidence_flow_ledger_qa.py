from pathlib import Path
from didactopus.evidence_flow_ledger_qa import evidence_flow_ledger_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str, projects_yaml: str, rubrics_yaml: str, evaluator_yaml: str, ledger_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text(projects_yaml, encoding="utf-8")
    (base / "rubrics.yaml").write_text(rubrics_yaml, encoding="utf-8")
    (base / "evaluator.yaml").write_text(evaluator_yaml, encoding="utf-8")
    (base / "mastery_ledger.yaml").write_text(ledger_yaml, encoding="utf-8")

def test_detects_missing_dimension_mapping(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations clearly]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [explanation exercise]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [explanation]\n",
        "rubrics:\n  - id: r1\n    title: Basic\n    criteria: [correctness]\n",
        "dimensions:\n  - name: explanation\n    description: quality of explanation\n",
        "entry_schema:\n  concept_id: str\n  score: float\n  confidence: float\n  last_updated: datetime\n",
    )
    result = evidence_flow_ledger_for_pack(tmp_path)
    assert any("dimension" in w.lower() for w in result["warnings"])


def test_optional_artifacts_absent_still_returns_summary(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations clearly]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [exercise]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [report]\n",
        "rubrics:\n  - id: r1\n    title: Basic\n    criteria: [correctness]\n",
        "",
        "",
    )
    result = evidence_flow_ledger_for_pack(tmp_path)
    assert "summary" in result
    assert isinstance(result["warnings"], list)
