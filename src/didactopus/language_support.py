from __future__ import annotations


LANGUAGE_LABELS = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "sw": "Swahili",
    "zh": "Chinese",
    "ja": "Japanese",
}


def language_label(language: str) -> str:
    return LANGUAGE_LABELS.get(language, language)


def response_language_instruction(language: str, source_language: str = "en") -> str:
    if language == source_language:
        return ""
    return (
        f" Respond in {language_label(language)}. Preserve key source-grounded concepts and caveats faithfully, "
        f"and make clear when you are explaining material whose source language is {language_label(source_language)}."
    )
