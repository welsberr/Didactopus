from pathlib import Path
import json

from didactopus.ocw_information_entropy_demo import run_ocw_information_entropy_demo


def test_ocw_information_entropy_demo_generates_pack_and_skill(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    summary = run_ocw_information_entropy_demo(
        course_source=root / "examples" / "ocw-information-entropy" / "course",
        source_inventory=root / "examples" / "ocw-information-entropy" / "sources.yaml",
        pack_dir=tmp_path / "pack",
        run_dir=tmp_path / "run",
        skill_dir=tmp_path / "skill",
    )

    assert (tmp_path / "pack" / "pack.yaml").exists()
    assert (tmp_path / "pack" / "pack_compliance_manifest.json").exists()
    assert (tmp_path / "pack" / "source_corpus.json").exists()
    assert (tmp_path / "run" / "capability_profile.json").exists()
    assert (tmp_path / "skill" / "SKILL.md").exists()
    assert summary["target_concept"].endswith("thermodynamics-and-entropy")
    assert summary["mastered_concepts"]
    assert summary["source_document_count"] >= 1
    assert summary["source_fragment_count"] >= 1

    corpus = json.loads((tmp_path / "pack" / "source_corpus.json").read_text(encoding="utf-8"))
    assert all(not Path(source["source_path"]).is_absolute() for source in corpus["sources"])
    assert any(source["source_path"].startswith("examples/ocw-information-entropy/course/") for source in corpus["sources"])

    graph = json.loads((tmp_path / "pack" / "knowledge_graph.json").read_text(encoding="utf-8"))
    source_nodes = [node for node in graph["nodes"] if node["type"] == "source"]
    assert all(not Path(node["source_path"]).is_absolute() for node in source_nodes)
    assert all(not node["id"].startswith("source::home-") for node in source_nodes)


def test_ocw_demo_accepts_directory_tree_sources(tmp_path: Path) -> None:
    source_dir = tmp_path / "course"
    source_dir.mkdir()
    (source_dir / "unit1.md").write_text(
        "# Course\n\n## Unit 1\n### Counting and Probability\n- Objective: Explain counting arguments.\nBody text.",
        encoding="utf-8",
    )
    (source_dir / "unit2.txt").write_text(
        "## Unit 2\n### Shannon Entropy\nObjective: Relate uncertainty and entropy.\nExercise: Compare two distributions.",
        encoding="utf-8",
    )
    sources = tmp_path / "sources.yaml"
    sources.write_text("sources: []\n", encoding="utf-8")

    summary = run_ocw_information_entropy_demo(
        course_source=source_dir,
        source_inventory=sources,
        pack_dir=tmp_path / "pack",
        run_dir=tmp_path / "run",
        skill_dir=tmp_path / "skill",
    )

    corpus = json.loads((tmp_path / "pack" / "source_corpus.json").read_text(encoding="utf-8"))
    assert summary["source_document_count"] == 2
    assert len(corpus["sources"]) == 2
    assert {source["source_path"] for source in corpus["sources"]} == {"course/unit1.md", "course/unit2.txt"}
    assert summary["course_source"] == "course"
    assert summary["pack_dir"] == "pack"
    assert any(fragment["lesson_title"] == "Shannon Entropy" for fragment in corpus["fragments"])
