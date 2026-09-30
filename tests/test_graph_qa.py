from pathlib import Path
from didactopus.graph_qa import graph_qa_for_pack

def make_pack(base: Path, concepts_yaml: str, roadmap_yaml: str):
    (base / "pack.yaml").write_text("name: p\ndisplay_name: P\nversion: 0.1.0\n", encoding="utf-8")
    (base / "concepts.yaml").write_text(concepts_yaml, encoding="utf-8")
    (base / "roadmap.yaml").write_text(roadmap_yaml, encoding="utf-8")
    (base / "projects.yaml").write_text("projects: []\n", encoding="utf-8")
    (base / "rubrics.yaml").write_text("rubrics: []\n", encoding="utf-8")

def test_cycle_and_isolated_detected(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: a\n    title: A\n    description: desc enough here\n    prerequisites: [c]\n  - id: b\n    title: B\n    description: desc enough here\n    prerequisites: [a]\n  - id: c\n    title: C\n    description: desc enough here\n    prerequisites: [b]\n  - id: iso\n    title: Iso\n    description: isolated description\n    prerequisites: []\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [a,b,c,iso]\n",
    )
    result = graph_qa_for_pack(tmp_path)
    assert result["status"] == "ok"
    assert result["summary"]["analysis_status"] == "complete"
    assert any("cycle" in w.lower() for w in result["warnings"])
    assert any("isolated" in w.lower() for w in result["warnings"])
    assert result["cyclic_components"] == [["a", "b", "c"]]

def test_bottleneck_detected(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: core\n    title: Core\n    description: central desc enough\n    prerequisites: []\n  - id: d1\n    title: D1\n    description: desc enough here\n    prerequisites: [core]\n  - id: d2\n    title: D2\n    description: desc enough here\n    prerequisites: [core]\n  - id: d3\n    title: D3\n    description: desc enough here\n    prerequisites: [core]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [core,d1,d2,d3]\n",
    )
    result = graph_qa_for_pack(tmp_path)
    assert any("high direct dependency count (3)" in w.lower() for w in result["warnings"])
    assert not any("downstream dependents" in w.lower() for w in result["warnings"])


def test_invalid_pack_is_not_reported_as_zero_graph_warnings(tmp_path: Path) -> None:
    result = graph_qa_for_pack(tmp_path)
    assert result["status"] == "invalid_input"
    assert result["summary"]["analysis_status"] == "not_run"
    assert result["summary"]["graph_warning_count"] is None
    assert any("Missing required file" in error for error in result["errors"])


def test_non_mapping_pack_entries_are_reported_not_crashed(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - malformed scalar\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: []\n",
    )
    result = graph_qa_for_pack(tmp_path)
    assert result["status"] == "invalid_input"
    assert result["summary"]["graph_warning_count"] is None
    assert any("entry at index 0 is not a mapping" in error for error in result["errors"])


def test_dangling_prerequisite_is_invalid_graph_input(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: a\n    title: A\n    description: enough detail here\n    prerequisites: [missing]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [a]\n",
    )
    result = graph_qa_for_pack(tmp_path)
    assert result["status"] == "invalid_input"
    assert result["summary"]["analysis_status"] == "not_run"
    assert any("references missing prerequisite" in error for error in result["errors"])


def test_cycle_members_and_blocked_descendants_are_separate(tmp_path: Path) -> None:
    make_pack(
        tmp_path,
        "concepts:\n  - id: a\n    title: A\n    description: enough detail here\n    prerequisites: [b]\n  - id: b\n    title: B\n    description: enough detail here\n    prerequisites: [a]\n  - id: c\n    title: C\n    description: enough detail here\n    prerequisites: [b]\n",
        "stages:\n  - id: s1\n    title: One\n    concepts: [a,b,c]\n",
    )
    result = graph_qa_for_pack(tmp_path)
    assert result["cyclic_components"] == [["a", "b"]]
    assert result["blocked_cycle_nodes"] == ["c"]
    assert result["summary"]["max_chain_length"] is None
