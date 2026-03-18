from didactopus.language_support import language_alignment_score, response_language_instruction, ui_text


def test_response_language_instruction_is_empty_for_source_language() -> None:
    assert response_language_instruction("en", "en") == ""


def test_response_language_instruction_mentions_target_language() -> None:
    instruction = response_language_instruction("es", "en")
    assert "Spanish" in instruction
    assert "English" in instruction


def test_ui_text_uses_translated_labels() -> None:
    assert ui_text("study_plan", "es") == "Plan de estudio"
    assert ui_text("evaluation_summary", "fr") == "Resume de l'evaluation"


def test_language_alignment_score_detects_non_english_markers() -> None:
    score, notes = language_alignment_score("La entropia y la capacidad del canal se comparan para el aprendiz.", "es")
    assert score == 1.0
    assert notes == []


def test_language_alignment_score_flags_wrong_language() -> None:
    score, notes = language_alignment_score("This response is still entirely in English.", "es")
    assert score == 0.0
    assert notes
