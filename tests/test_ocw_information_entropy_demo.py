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


def test_ocw_demo_can_apply_wolfe_snippet_augmentation(tmp_path: Path) -> None:
    source_dir = tmp_path / "course"
    source_dir.mkdir()
    (source_dir / "unit1.md").write_text(
        "# Course\n\n## Unit 1\n### Thermodynamics and Entropy\n- Objective: Explain entropy.\nEntropy links uncertainty to physics.",
        encoding="utf-8",
    )
    sources = tmp_path / "sources.yaml"
    sources.write_text("sources: []\n", encoding="utf-8")

    wolfe_dir = tmp_path / "wolfe"
    wolfe_dir.mkdir()
    (wolfe_dir / "snippet.md").write_text(
        "# Wolfe Snippet\n\n## Augmentation\n### Entropy Comparison\n- Objective: Compare Shannon entropy with thermodynamic entropy.\nThe two notions differ in interpretation even when the mathematics overlaps.",
        encoding="utf-8",
    )
    wolfe_sources = tmp_path / "wolfe-sources.yaml"
    wolfe_sources.write_text(
        "\n".join(
            [
                "sources:",
                "  - source_id: wolfe-local-snippet",
                "    title: Wolfe local snippet",
                "    url: file:///local/wolfe/snippet",
                "    publisher: Local Library",
                "    creator: Local Search",
                "    license_id: local-only",
                "    license_url: https://example.invalid/local-only",
                "    retrieved_at: '2026-05-08'",
                "    adapted: false",
                "    attribution_text: Local Wolfe-derived snippet for private evaluation.",
                "    excluded_from_upstream_license: true",
                "    exclusion_notes: Local-only experimental augmentation.",
            ]
        ),
        encoding="utf-8",
    )
    (wolfe_dir / "concept-alignment.yaml").write_text(
        "\n".join(
            [
                "alignments:",
                "  - source_title: Entropy Comparison",
                "    target_title: Thermodynamics and Entropy",
            ]
        ),
        encoding="utf-8",
    )

    summary = run_ocw_information_entropy_demo(
        course_source=source_dir,
        source_inventory=sources,
        pack_dir=tmp_path / "pack",
        run_dir=tmp_path / "run",
        skill_dir=tmp_path / "skill",
        wolfe_snippets_dir=wolfe_dir,
        wolfe_source_inventory=wolfe_sources,
    )

    bundle = json.loads((tmp_path / "pack" / "groundrecall_query_bundle.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "pack" / "pack_compliance_manifest.json").read_text(encoding="utf-8"))
    concept_titles = [item["title"] for item in (json.loads((tmp_path / "pack" / "knowledge_graph.json").read_text(encoding="utf-8"))["nodes"]) if item.get("type") == "concept"]
    assert summary["wolfe_source_document_count"] == 1
    assert summary["source_document_count"] == 2
    assert "wolfe-local-snippet" in manifest["derived_from_sources"]
    assert bundle["bundle_kind"] == "groundrecall_query_bundle"
    assert "Entropy Comparison" not in concept_titles


def test_ocw_demo_can_load_augmentation_bundle(tmp_path: Path) -> None:
    source_dir = tmp_path / "course"
    source_dir.mkdir()
    (source_dir / "unit1.md").write_text(
        "# Course\n\n## Unit 1\n### Thermodynamics and Entropy\n- Objective: Explain entropy.\nEntropy links uncertainty to physics.",
        encoding="utf-8",
    )
    sources = tmp_path / "sources.yaml"
    sources.write_text("sources: []\n", encoding="utf-8")

    bundle_dir = tmp_path / "bundle"
    snippets_dir = bundle_dir / "snippets"
    snippets_dir.mkdir(parents=True)
    (snippets_dir / "snippet.md").write_text(
        "# Wolfe Snippet\n\n## Augmentation\n### Entropy Comparison\n- Objective: Compare Shannon entropy with thermodynamic entropy.\nThe two notions differ in interpretation even when the mathematics overlaps.",
        encoding="utf-8",
    )
    (bundle_dir / "sources.yaml").write_text(
        "\n".join(
            [
                "sources:",
                "  - source_id: wolfe-local-snippet",
                "    title: Wolfe local snippet",
                "    url: file:///local/wolfe/snippet",
                "    publisher: Local Library",
                "    creator: Local Search",
                "    license_id: local-only",
                "    license_url: https://example.invalid/local-only",
                "    retrieved_at: '2026-05-08'",
                "    adapted: false",
                "    attribution_text: Local Wolfe-derived snippet for private evaluation.",
                "    excluded_from_upstream_license: true",
                "    exclusion_notes: Local-only experimental augmentation.",
            ]
        ),
        encoding="utf-8",
    )
    (snippets_dir / "concept-alignment.yaml").write_text(
        "\n".join(
            [
                "alignments:",
                "  - source_title: Entropy Comparison",
                "    target_title: Thermodynamics and Entropy",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "bundle.yaml").write_text(
        "\n".join(
            [
                "title: OCW Wolfe Bundle",
                "snippets_dir: snippets",
                "source_inventory: sources.yaml",
                "concept_alignment: snippets/concept-alignment.yaml",
            ]
        ),
        encoding="utf-8",
    )

    summary = run_ocw_information_entropy_demo(
        course_source=source_dir,
        source_inventory=sources,
        pack_dir=tmp_path / "pack",
        run_dir=tmp_path / "run",
        skill_dir=tmp_path / "skill",
        augmentation_bundle=bundle_dir,
    )

    assert summary["augmentation_bundle"].endswith("/bundle")
    assert summary["augmentation_bundle_title"] == "OCW Wolfe Bundle"
    assert summary["wolfe_source_document_count"] == 1
