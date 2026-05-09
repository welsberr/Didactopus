from pathlib import Path

from didactopus.augmentation_bundle import load_augmentation_bundle


def test_load_augmentation_bundle_defaults(tmp_path: Path) -> None:
    (tmp_path / "snippets").mkdir()
    (tmp_path / "snippets" / "concept-alignment.yaml").write_text("alignments: []\n", encoding="utf-8")
    (tmp_path / "wolfe-sources.yaml").write_text("sources: []\n", encoding="utf-8")

    payload = load_augmentation_bundle(tmp_path)
    assert payload["snippets_dir"].endswith("/snippets")
    assert payload["source_inventory"].endswith("/wolfe-sources.yaml")
    assert payload["concept_alignment"].endswith("/snippets/concept-alignment.yaml")


def test_load_augmentation_bundle_manifest_overrides_paths(tmp_path: Path) -> None:
    (tmp_path / "extras").mkdir()
    (tmp_path / "extras" / "map.yaml").write_text("alignments: []\n", encoding="utf-8")
    (tmp_path / "inventory.yaml").write_text("sources: []\n", encoding="utf-8")
    (tmp_path / "bundle.yaml").write_text(
        "\n".join(
            [
                "title: Demo Bundle",
                "snippets_dir: extras",
                "source_inventory: inventory.yaml",
                "concept_alignment: extras/map.yaml",
            ]
        ),
        encoding="utf-8",
    )

    payload = load_augmentation_bundle(tmp_path)
    assert payload["title"] == "Demo Bundle"
    assert payload["snippets_dir"].endswith("/extras")
    assert payload["source_inventory"].endswith("/inventory.yaml")
    assert payload["concept_alignment"].endswith("/extras/map.yaml")
