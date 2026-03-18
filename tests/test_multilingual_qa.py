from pathlib import Path

from didactopus.multilingual_qa import (
    load_multilingual_qa_spec,
    multilingual_qa_for_pack,
    multilingual_qa_for_text,
    round_trip_warning_for_phrases,
)


def test_load_multilingual_qa_spec_reads_ocw_pack() -> None:
    spec = load_multilingual_qa_spec("domain-packs/mit-ocw-information-entropy")
    assert spec["source_language"] == "en"
    assert "es" in spec["targets"]
    assert "fr" in spec["targets"]


def test_multilingual_qa_for_text_accepts_spanish_preservation() -> None:
    spec = load_multilingual_qa_spec("domain-packs/mit-ocw-information-entropy")
    result = multilingual_qa_for_text(
        spec,
        language="es",
        text="La entropía de Shannon no es idéntica a la entropía termodinámica, y la capacidad del canal impone otro límite.",
    )
    assert result["summary"]["matched_term_count"] >= 2
    assert result["summary"]["matched_caveat_count"] == 1
    assert result["summary"]["confusion_hit_count"] == 0


def test_multilingual_qa_for_text_flags_confusion() -> None:
    spec = load_multilingual_qa_spec("domain-packs/mit-ocw-information-entropy")
    result = multilingual_qa_for_text(
        spec,
        language="es",
        text="La entropía de Shannon es idéntica a la entropía termodinámica.",
    )
    assert result["summary"]["confusion_hit_count"] == 1
    assert any("forbidden multilingual confusion" in warning.lower() for warning in result["warnings"])


def test_multilingual_qa_for_pack_handles_missing_spec(tmp_path: Path) -> None:
    result = multilingual_qa_for_pack(tmp_path, language="es", text="Texto de prueba.")
    assert any("no multilingual qa spec" in warning.lower() for warning in result["warnings"])


def test_round_trip_warning_for_phrases_flags_drift() -> None:
    result = round_trip_warning_for_phrases(
        ["Shannon entropy", "channel capacity"],
        "This back translation only preserved Shannon entropy.",
    )
    assert result["summary"]["round_trip_warning_count"] == 1
    assert result["summary"]["drifted_phrases"] == ["channel capacity"]
