from pathlib import Path

import yaml

from didactopus.multilingual_qa_review import promote_multilingual_qa_entries


def test_promote_multilingual_qa_entries_writes_curated_spec(tmp_path: Path) -> None:
    seed = tmp_path / "multilingual_qa.seed.yaml"
    seed.write_text(
        yaml.safe_dump(
            {
                "source_language": "en",
                "targets": {
                    "es": {
                        "required_terms": [
                            {"id": "shannon-entropy", "accepted": ["Shannon entropy"]},
                            {"id": "channel-capacity", "accepted": ["channel capacity"]},
                        ],
                        "required_caveats": [
                            {"id": "not-identical", "accepted": ["Shannon entropy is not identical to thermodynamic entropy"]},
                        ],
                        "forbidden_confusions": [
                            {"id": "identical-confusion", "patterns": ["Shannon entropy is identical to thermodynamic entropy"]},
                        ],
                    }
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    out = tmp_path / "multilingual_qa.yaml"
    payload = promote_multilingual_qa_entries(
        seed_path=seed,
        out_path=out,
        language="es",
        required_term_ids=["shannon-entropy"],
        required_caveat_ids=["not-identical"],
        forbidden_confusion_ids=["identical-confusion"],
        canonical_round_trip_ids=["shannon-entropy", "not-identical"],
    )

    assert out.exists()
    assert payload["review_status"] == "curated"
    target = payload["targets"]["es"]
    assert len(target["required_terms"]) == 1
    assert target["required_terms"][0]["round_trip_required"] is True
    assert target["required_terms"][0]["round_trip_source"] == "Shannon entropy"
    assert target["required_caveats"][0]["round_trip_required"] is True


def test_promote_multilingual_qa_entries_preserves_other_languages(tmp_path: Path) -> None:
    seed = tmp_path / "multilingual_qa.seed.yaml"
    seed.write_text(
        yaml.safe_dump(
            {
                "source_language": "en",
                "targets": {
                    "es": {"required_terms": [{"id": "shannon-entropy", "accepted": ["Shannon entropy"]}]},
                    "fr": {"required_terms": [{"id": "entropie", "accepted": ["Shannon entropy"]}]},
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    out = tmp_path / "multilingual_qa.yaml"
    out.write_text(
        yaml.safe_dump(
            {
                "source_language": "en",
                "targets": {
                    "fr": {"required_terms": [{"id": "entropie", "accepted": ["entropie de Shannon"]}]}
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    payload = promote_multilingual_qa_entries(
        seed_path=seed,
        out_path=out,
        language="es",
        required_term_ids=["shannon-entropy"],
    )
    assert "fr" in payload["targets"]
    assert payload["targets"]["fr"]["required_terms"][0]["id"] == "entropie"
