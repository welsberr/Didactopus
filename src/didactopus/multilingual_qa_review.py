from __future__ import annotations

from pathlib import Path

import yaml


def _load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _index_entries(entries: list[dict]) -> dict[str, dict]:
    return {str(entry.get("id", "")): dict(entry) for entry in entries if entry.get("id")}


def _select_entries(seed_entries: list[dict], selected_ids: list[str], canonical_ids: set[str]) -> list[dict]:
    index = _index_entries(seed_entries)
    selected = []
    for entry_id in selected_ids:
        if entry_id not in index:
            continue
        entry = dict(index[entry_id])
        if entry_id in canonical_ids:
            entry["round_trip_required"] = True
            accepted = entry.get("accepted", []) or []
            if accepted and "round_trip_source" not in entry:
                entry["round_trip_source"] = str(accepted[0])
        selected.append(entry)
    return selected


def promote_multilingual_qa_entries(
    *,
    seed_path: str | Path,
    out_path: str | Path,
    language: str,
    required_term_ids: list[str] | None = None,
    required_caveat_ids: list[str] | None = None,
    forbidden_confusion_ids: list[str] | None = None,
    canonical_round_trip_ids: list[str] | None = None,
) -> dict:
    seed = _load_yaml(seed_path)
    curated = _load_yaml(out_path)
    target_seed = ((seed.get("targets", {}) or {}).get(language, {})) or {}
    target_curated = ((curated.get("targets", {}) or {}).get(language, {})) or {}
    canonical_ids = set(canonical_round_trip_ids or [])

    promoted_terms = _select_entries(target_seed.get("required_terms", []) or [], required_term_ids or [], canonical_ids)
    promoted_caveats = _select_entries(target_seed.get("required_caveats", []) or [], required_caveat_ids or [], canonical_ids)
    promoted_confusions = _select_entries(target_seed.get("forbidden_confusions", []) or [], forbidden_confusion_ids or [], canonical_ids)

    curated_targets = dict(curated.get("targets", {}) or {})
    curated_targets[language] = {
        "required_terms": promoted_terms or target_curated.get("required_terms", []) or [],
        "required_caveats": promoted_caveats or target_curated.get("required_caveats", []) or [],
        "forbidden_confusions": promoted_confusions or target_curated.get("forbidden_confusions", []) or [],
    }

    payload = {
        "source_language": seed.get("source_language", curated.get("source_language", "en")),
        "review_status": "curated",
        "promoted_from_seed": str(seed_path),
        "targets": curated_targets,
    }
    out = Path(out_path)
    out.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Promote selected multilingual QA seed entries into a curated spec.")
    parser.add_argument("--seed", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--required-term-id", action="append", default=[])
    parser.add_argument("--required-caveat-id", action="append", default=[])
    parser.add_argument("--forbidden-confusion-id", action="append", default=[])
    parser.add_argument("--canonical-round-trip-id", action="append", default=[])
    args = parser.parse_args()
    promote_multilingual_qa_entries(
        seed_path=args.seed,
        out_path=args.out,
        language=args.language,
        required_term_ids=args.required_term_id,
        required_caveat_ids=args.required_caveat_id,
        forbidden_confusion_ids=args.forbidden_confusion_id,
        canonical_round_trip_ids=args.canonical_round_trip_id,
    )
    print(yaml.safe_dump({"written": args.out, "language": args.language}, sort_keys=False))


if __name__ == "__main__":
    main()
