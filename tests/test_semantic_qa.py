from pathlib import Path
from didactopus.semantic_qa import semantic_qa_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (base / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")

def test_semantic_warnings_detected(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Prior and Posterior\n    description: Beliefs before and after evidence.\n  - id: c2\n    title: Posterior Analysis\n    description: Beliefs before and after evidence.\n",
        "stages:\n  - id: s1\n    title: Foundations\n    concepts: [c1]\n  - id: s2\n    title: Advanced Inference\n    concepts: [c2]\n",
    )
    result = semantic_qa_for_pack(tmp_path)
    assert len(result["warnings"]) >= 1

def test_semantic_summary_exists(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: c1\n    title: Bayes Prior\n    description: Prior beliefs before evidence in a probabilistic model.\n",
        "stages:\n  - id: s1\n    title: Prior Beliefs\n    concepts: [c1]\n",
    )
    result = semantic_qa_for_pack(tmp_path)
    assert "semantic_warning_count" in result["summary"]
