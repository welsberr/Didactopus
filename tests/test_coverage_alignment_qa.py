from pathlib import Path
from didactopus.coverage_alignment_qa import coverage_alignment_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str, projects_yaml: str, rubrics_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text(projects_yaml, encoding="utf-8")
    (base / "rubrics.yaml").write_text(rubrics_yaml, encoding="utf-8")

def test_detects_uncovered_concepts(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations]\n  - id: c2\n    title: Detached Topic\n    description: enough description here\n    mastery_signals: [Explain detached topic]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [Explain foundations]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [short report]\n",
        "rubrics:\n  - id: r1\n    title: Basic\n    criteria: [correctness]\n",
    )
    result = coverage_alignment_for_pack(tmp_path)
    assert any("c2" in w for w in result["warnings"])


def test_covered_concepts_do_not_warn(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: enough description here\n    mastery_signals: [Explain foundations]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [Explain foundations]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [short report]\n",
        "rubrics:\n  - id: r1\n    title: Basic\n    criteria: [correctness]\n",
    )
    result = coverage_alignment_for_pack(tmp_path)
    assert result["warnings"] == []
