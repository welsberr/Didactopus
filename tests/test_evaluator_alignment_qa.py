from pathlib import Path
from didactopus.evaluator_alignment_qa import evaluator_alignment_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str, projects_yaml: str, rubrics_yaml: str, evaluator_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text(projects_yaml, encoding="utf-8")
    (base / "rubrics.yaml").write_text(rubrics_yaml, encoding="utf-8")
    (base / "evaluator.yaml").write_text(evaluator_yaml, encoding="utf-8")

def test_detects_uncovered_mastery_signals(tmp_path: Path) -> None:
    make_pack(tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations clearly]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [Explain foundations]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [report]\n",
        "rubrics:\n  - id: r1\n    title: Basic\n    criteria: [correctness]\n",
        "dimensions:\n  - name: typography\n    description: page polish\n")
    result = evaluator_alignment_for_pack(tmp_path)
    assert any('Mastery signal' in w for w in result['warnings'])
