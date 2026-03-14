from pathlib import Path
from didactopus.path_quality_qa import path_quality_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str, projects_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text(projects_yaml, encoding="utf-8")
    (base / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")

def test_detects_checkpoint_and_unassessed_issues(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: foundations description enough\n    prerequisites: []\n  - id: c2\n    title: Advanced Inference\n    description: advanced inference description enough\n    prerequisites: [c1]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1,c2]\n    checkpoint: []\n",
        "projects: []\n",
    )
    result = path_quality_for_pack(tmp_path)
    assert any("no checkpoint" in w.lower() for w in result["warnings"])
    assert any("not visibly assessed" in w.lower() for w in result["warnings"])


def test_assessed_path_has_no_warnings(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Foundations\n    description: foundations description enough\n    prerequisites: []\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [c1]\n    checkpoint: [quiz]\n",
        "projects:\n  - id: p1\n    title: Project\n    prerequisites: [c1]\n    deliverables: [report]\n",
    )
    result = path_quality_for_pack(tmp_path)
    assert result["warnings"] == []
