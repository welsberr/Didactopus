from __future__ import annotations

import json
from pathlib import Path

import yaml

from .pack_validator import load_pack_artifacts


def _normalize_phrase(text: str) -> str:
    return " ".join(str(text).replace(":", " ").replace("-", " ").split()).strip()


def _candidate_languages(languages: list[str] | None) -> list[str]:
    return list(languages) if languages else ["es", "fr"]


def _seed_required_terms(concepts: list[dict]) -> list[dict]:
    seeded = []
    seen = set()
    for concept in concepts:
        title = str(concept.get("title", "")).strip()
        concept_id = str(concept.get("id", "")).strip()
        if not title or not concept_id:
            continue
        normalized = _normalize_phrase(title)
        if len(normalized.split()) < 2:
            continue
        if concept_id in seen:
            continue
        seen.add(concept_id)
        seeded.append(
            {
                "id": concept_id,
                "accepted": [normalized],
            }
        )
    return seeded[:12]


def _seed_required_caveats(source_corpus: dict) -> list[dict]:
    caveats = []
    seen = set()
    for fragment in source_corpus.get("fragments", []) or []:
        texts = [fragment.get("text", "")]
        texts.extend(fragment.get("objectives", []) or [])
        texts.extend(fragment.get("exercises", []) or [])
        for text in texts:
            lowered = str(text).lower()
            if "not identical" in lowered or "differs from" in lowered or "careful interpretation" in lowered:
                lesson_title = _normalize_phrase(fragment.get("lesson_title", "lesson"))
                caveat_id = lesson_title.lower().replace(" ", "-")[:48] or "caveat"
                if caveat_id in seen:
                    continue
                seen.add(caveat_id)
                caveats.append(
                    {
                        "id": caveat_id,
                        "accepted": [_normalize_phrase(text)],
                    }
                )
    return caveats[:6]


def _seed_forbidden_confusions(required_caveats: list[dict]) -> list[dict]:
    confusions = []
    for caveat in required_caveats:
        accepted = caveat.get("accepted", []) or []
        if not accepted:
            continue
        phrase = str(accepted[0])
        lowered = phrase.lower()
        if "not identical" in lowered:
            confusion = phrase.replace("not identical", "identical")
        elif "differs from" in lowered:
            confusion = phrase.replace("differs from", "is identical to")
        else:
            continue
        confusions.append(
            {
                "id": f"{caveat['id']}-confusion",
                "patterns": [_normalize_phrase(confusion)],
            }
        )
    return confusions[:6]


def generate_multilingual_qa_seed(
    source_dir: str | Path,
    *,
    languages: list[str] | None = None,
) -> dict:
    source_dir = Path(source_dir)
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        raise ValueError(f"Cannot seed multilingual QA for invalid pack directory: {source_dir}")

    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    source_corpus_path = source_dir / "source_corpus.json"
    source_corpus = json.loads(source_corpus_path.read_text(encoding="utf-8")) if source_corpus_path.exists() else {"fragments": []}
    required_terms = _seed_required_terms(concepts)
    required_caveats = _seed_required_caveats(source_corpus)
    forbidden_confusions = _seed_forbidden_confusions(required_caveats)

    targets = {}
    for language in _candidate_languages(languages):
        targets[language] = {
            "required_terms": required_terms,
            "required_caveats": required_caveats,
            "forbidden_confusions": forbidden_confusions,
        }

    return {
        "source_language": "en",
        "generated_by": "didactopus.multilingual_qa_seed",
        "review_status": "draft-seed",
        "targets": targets,
    }


def write_multilingual_qa_seed(
    source_dir: str | Path,
    *,
    out_path: str | Path | None = None,
    languages: list[str] | None = None,
) -> Path:
    source_dir = Path(source_dir)
    payload = generate_multilingual_qa_seed(source_dir, languages=languages)
    out_path = Path(out_path) if out_path is not None else source_dir / "multilingual_qa.seed.yaml"
    out_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8")
    return out_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate a starter multilingual QA spec from a Didactopus pack.")
    parser.add_argument("pack_dir")
    parser.add_argument("--out", default=None)
    parser.add_argument("--languages", nargs="*", default=None)
    args = parser.parse_args()
    out_path = write_multilingual_qa_seed(args.pack_dir, out_path=args.out, languages=args.languages)
    print(json.dumps({"written": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
