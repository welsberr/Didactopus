from pathlib import Path
import json

from didactopus.augmentation_bundle_probe import probe_augmentation_bundle


def test_probe_augmentation_bundle_reports_hub_and_related_matches(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    snippets = bundle / "snippets"
    snippets.mkdir(parents=True)
    (bundle / "bundle.yaml").write_text(
        "\n".join(
            [
                "title: Demo Bundle",
                "snippets_dir: snippets",
                "source_inventory: sources.yaml",
                "concept_alignment: snippets/concept-alignment.yaml",
            ]
        ),
        encoding="utf-8",
    )
    (bundle / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    (snippets / "a.md").write_text("# A\n", encoding="utf-8")
    (snippets / "b.md").write_text("# B\n", encoding="utf-8")
    (snippets / "concept-alignment.yaml").write_text(
        "\n".join(
            [
                "alignments:",
                "  - source_title: Entropy Comparison",
                "    target_title: Thermodynamics and Entropy",
                "  - source_title: Drift Note",
                "    target_title: Genetic drift",
                "  - source_title: Extra",
                "    target_title: Missing",
            ]
        ),
        encoding="utf-8",
    )
    groundrecall_bundle = tmp_path / "groundrecall_query_bundle.json"
    groundrecall_bundle.write_text(
        json.dumps(
            {
                "concept": {"title": "Thermodynamics and Entropy"},
                "related_concepts": [{"id": "concept::genetic-drift", "label": "Genetic drift"}, {"label": "Natural selection"}],
            }
        ),
        encoding="utf-8",
    )

    payload = probe_augmentation_bundle(bundle, groundrecall_bundle)
    assert payload["snippet_count"] == 2
    assert payload["matched_hub_alignment_count"] == 1
    assert payload["matched_related_alignment_count"] == 1
    assert payload["unmatched_alignment_count"] == 1
