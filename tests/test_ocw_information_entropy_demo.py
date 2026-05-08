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
    assert (tmp_path / "pack" / "groundrecall_query_bundle.json").exists()
    assert (tmp_path / "pack" / "notebook_page.json").exists()
    assert (tmp_path / "run" / "capability_profile.json").exists()
    assert (tmp_path / "skill" / "SKILL.md").exists()
    assert summary["target_concept"].endswith("thermodynamics-and-entropy")
    assert summary["groundrecall_concept_ref"] == "Thermodynamics and Entropy"
    assert summary["groundrecall_bundle_included"] is True
    assert summary["mastered_concepts"]
    assert summary["source_document_count"] >= 1
    assert summary["source_fragment_count"] >= 1


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
    groundrecall_bundle = json.loads((tmp_path / "pack" / "groundrecall_query_bundle.json").read_text(encoding="utf-8"))
    assert summary["source_document_count"] == 2
    assert len(corpus["sources"]) == 2
    assert groundrecall_bundle["bundle_kind"] == "groundrecall_query_bundle"
    assert any(fragment["lesson_title"] == "Shannon Entropy" for fragment in corpus["fragments"])
