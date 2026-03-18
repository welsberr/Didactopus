from pathlib import Path

import yaml

from didactopus.multilingual_qa_seed import generate_multilingual_qa_seed, write_multilingual_qa_seed


def test_generate_multilingual_qa_seed_uses_pack_content() -> None:
    payload = generate_multilingual_qa_seed("domain-packs/mit-ocw-information-entropy", languages=["es"])
    assert payload["source_language"] == "en"
    assert payload["review_status"] == "draft-seed"
    assert "es" in payload["targets"]
    target = payload["targets"]["es"]
    assert target["required_terms"]
    assert any(item["id"] == "shannon-entropy" for item in target["required_terms"])
    assert target["required_caveats"]


def test_write_multilingual_qa_seed_writes_yaml(tmp_path: Path) -> None:
    out = write_multilingual_qa_seed(
        "domain-packs/mit-ocw-information-entropy",
        out_path=tmp_path / "multilingual_qa.seed.yaml",
        languages=["es", "fr"],
    )
    assert out.exists()
    written = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert set(written["targets"]) == {"es", "fr"}
