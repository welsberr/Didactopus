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

UI_STRINGS = {
    "en": {
        "didactopus_learner_session": "Didactopus Learner Session",
        "learner_goal": "Learner goal",
        "source_language": "Source language",
        "output_language": "Output language",
        "study_plan": "Study Plan",
        "conversation": "Conversation",
        "evaluation_summary": "Evaluation Summary",
        "verdict": "Verdict",
        "aggregated_dimensions": "Aggregated dimensions",
        "follow_up": "Follow-up",
        "status": "Status",
        "prerequisites": "Prerequisites",
        "supporting_lessons": "Supporting lessons",
        "grounding_fragments": "Grounding fragments",
        "source_fragment": "Source fragment",
        "skip_to_session": "Skip to learner session",
        "screen_reader_note": "This page is structured for keyboard and screen-reader use. It presents the learner goal, study plan, grounded source fragments, and conversation turns in reading order.",
    },
    "es": {
        "didactopus_learner_session": "Sesion de aprendizaje de Didactopus",
        "learner_goal": "Objetivo del aprendiz",
        "source_language": "Idioma de origen",
        "output_language": "Idioma de salida",
        "study_plan": "Plan de estudio",
        "conversation": "Conversacion",
        "evaluation_summary": "Resumen de evaluacion",
        "verdict": "Veredicto",
        "aggregated_dimensions": "Dimensiones agregadas",
        "follow_up": "Siguiente paso",
        "status": "Estado",
        "prerequisites": "Prerrequisitos",
        "supporting_lessons": "Lecciones de apoyo",
        "grounding_fragments": "Fragmentos de fundamento",
        "source_fragment": "Fragmento de fuente",
        "skip_to_session": "Saltar a la sesion de aprendizaje",
        "screen_reader_note": "Esta pagina esta estructurada para uso con teclado y lector de pantalla. Presenta el objetivo del aprendiz, el plan de estudio, los fragmentos de fundamento y los turnos de conversacion en orden de lectura.",
    },
    "fr": {
        "didactopus_learner_session": "Session d'apprentissage Didactopus",
        "learner_goal": "Objectif de l'apprenant",
        "source_language": "Langue source",
        "output_language": "Langue de sortie",
        "study_plan": "Plan d'etude",
        "conversation": "Conversation",
        "evaluation_summary": "Resume de l'evaluation",
        "verdict": "Verdict",
        "aggregated_dimensions": "Dimensions agregees",
        "follow_up": "Etape suivante",
        "status": "Statut",
        "prerequisites": "Prerquis",
        "supporting_lessons": "Lecons de soutien",
        "grounding_fragments": "Fragments d'ancrage",
        "source_fragment": "Fragment source",
        "skip_to_session": "Aller a la session d'apprentissage",
        "screen_reader_note": "Cette page est structuree pour une utilisation au clavier et avec un lecteur d'ecran. Elle presente l'objectif de l'apprenant, le plan d'etude, les fragments d'ancrage et les tours de conversation dans l'ordre de lecture.",
    },
}

LANGUAGE_MARKERS = {
    "es": (" el ", " la ", " de ", " y ", " que ", " para ", " no ", "una ", "un "),
    "fr": (" le ", " la ", " de ", " et ", " que ", " pour ", " pas ", "une ", "un "),
    "de": (" der ", " die ", " und ", " nicht ", " ist ", " fur "),
    "pt": (" o ", " a ", " de ", " e ", " para ", " nao "),
    "it": (" il ", " la ", " di ", " e ", " per ", " non "),
}


def language_label(language: str) -> str:
    return LANGUAGE_LABELS.get(language, language)


def ui_text(key: str, language: str) -> str:
    table = UI_STRINGS.get(language, UI_STRINGS["en"])
    return table.get(key, UI_STRINGS["en"].get(key, key))


def response_language_instruction(language: str, source_language: str = "en") -> str:
    if language == source_language:
        return ""
    return (
        f" Respond in {language_label(language)}. Preserve key source-grounded concepts and caveats faithfully, "
        f"and make clear when you are explaining material whose source language is {language_label(source_language)}."
    )


def language_alignment_score(text: str, language: str) -> tuple[float, list[str]]:
    if language == "en":
        return 1.0, []
    lowered = f" {text.lower()} "
    markers = LANGUAGE_MARKERS.get(language)
    if markers is None:
        return 0.5, [f"No language-specific heuristic markers are defined for {language} yet."]
    marker_hits = sum(1 for marker in markers if marker in lowered)
    if marker_hits >= 2:
        return 1.0, []
    if marker_hits == 1:
        return 0.6, [f"Only weak evidence that the response is actually in {language_label(language)}."]
    return 0.0, [f"Response does not appear to be in {language_label(language)}."]
