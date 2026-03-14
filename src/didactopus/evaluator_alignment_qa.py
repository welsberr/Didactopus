from __future__ import annotations

import re

from .pack_validator import load_pack_artifacts


def _tok(text: str) -> set[str]:
    return {part for part in re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split() if part}


def evaluator_alignment_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"evaluator_warning_count": 0}}

    arts = loaded["artifacts"]
    concepts = arts["concepts"].get("concepts", []) or []
    evaluator = arts.get("evaluator", {}) or {}
    dimensions = evaluator.get("dimensions", []) or []
    dimension_tokens = set().union(
        *[
            _tok(dim if isinstance(dim, str) else dim.get("name", ""))
            for dim in dimensions
        ]
    ) if dimensions else set()

    warnings = []
    for concept in concepts:
        for signal in concept.get("mastery_signals", []) or []:
            signal_tokens = _tok(signal)
            if signal_tokens and signal_tokens.isdisjoint(dimension_tokens):
                warnings.append(
                    f"Mastery signal for concept '{concept.get('id')}' is not aligned to declared evaluator dimensions."
                )

    return {
        "warnings": warnings,
        "summary": {
            "evaluator_warning_count": len(warnings),
            "dimension_count": len(dimensions),
        },
    }
