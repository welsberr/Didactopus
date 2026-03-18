from __future__ import annotations

from pathlib import Path

import yaml


def _contains_non_negated_pattern(lowered: str, pattern: str) -> bool:
    start = lowered.find(pattern)
    while start != -1:
        prefix = lowered[max(0, start - 4):start]
        if not prefix.endswith("no "):
            return True
        start = lowered.find(pattern, start + 1)
    return False


def load_multilingual_qa_spec(source_dir: str | Path) -> dict:
    source = Path(source_dir)
    path = source / "multilingual_qa.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def multilingual_qa_for_text(spec: dict, *, language: str, text: str) -> dict:
    targets = spec.get("targets", {}) or {}
    target = targets.get(language, {}) or {}
    warnings: list[str] = []
    summary = {
        "language": language,
        "required_term_count": 0,
        "matched_term_count": 0,
        "required_caveat_count": 0,
        "matched_caveat_count": 0,
        "forbidden_confusion_count": 0,
        "confusion_hit_count": 0,
    }
    if not target:
        warnings.append(f"No multilingual QA spec is defined for language '{language}'.")
        return {"warnings": warnings, "summary": summary}

    lowered = text.lower()

    required_terms = target.get("required_terms", []) or []
    summary["required_term_count"] = len(required_terms)
    for term in required_terms:
        accepted = [str(item).lower() for item in term.get("accepted", []) or []]
        if any(candidate in lowered for candidate in accepted):
            summary["matched_term_count"] += 1
        else:
            warnings.append(f"Missing required multilingual term '{term.get('id', 'unknown')}' for language '{language}'.")

    required_caveats = target.get("required_caveats", []) or []
    summary["required_caveat_count"] = len(required_caveats)
    for caveat in required_caveats:
        accepted = [str(item).lower() for item in caveat.get("accepted", []) or []]
        if any(candidate in lowered for candidate in accepted):
            summary["matched_caveat_count"] += 1
        else:
            warnings.append(f"Missing required multilingual caveat '{caveat.get('id', 'unknown')}' for language '{language}'.")

    forbidden_confusions = target.get("forbidden_confusions", []) or []
    summary["forbidden_confusion_count"] = len(forbidden_confusions)
    for confusion in forbidden_confusions:
        patterns = [str(item).lower() for item in confusion.get("patterns", []) or []]
        if any(_contains_non_negated_pattern(lowered, pattern) for pattern in patterns):
            summary["confusion_hit_count"] += 1
            warnings.append(f"Detected forbidden multilingual confusion '{confusion.get('id', 'unknown')}' for language '{language}'.")

    return {"warnings": warnings, "summary": summary}


def multilingual_qa_for_pack(source_dir: str | Path, *, language: str, text: str) -> dict:
    spec = load_multilingual_qa_spec(source_dir)
    return multilingual_qa_for_text(spec, language=language, text=text)


def round_trip_warning_for_phrases(
    source_phrases: list[str],
    back_translated_text: str,
) -> dict:
    lowered = back_translated_text.lower()
    warnings: list[str] = []
    drifted: list[str] = []
    for phrase in source_phrases:
        normalized = str(phrase).strip().lower()
        if not normalized:
            continue
        if normalized not in lowered:
            warnings.append(f"Round-trip translation did not preserve source phrase '{phrase}'.")
            drifted.append(phrase)
    return {
        "warnings": warnings,
        "summary": {
            "source_phrase_count": len([phrase for phrase in source_phrases if str(phrase).strip()]),
            "round_trip_warning_count": len(warnings),
            "drifted_phrases": drifted,
        },
    }
