from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_DEFINITION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bdefined as\b",
        r"\brefers to\b",
        r"\bmeans\b",
        r"\bis (?:a|an|the)\b",
        r"\bdescribes\b",
        r"\bconsists of\b",
    )
]
_DISTINCTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bversus\b|\bvs\.?\b",
        r"\bnot\b.+\bbut\b",
        r"\bdistinguish\b",
        r"\bcontrast\b",
        r"\bcompare\b",
        r"\bdifferent from\b",
        r"\bdoes not imply\b",
        r"\bnot identical\b",
    )
]
_QUALIFICATION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bhowever\b",
        r"\balthough\b",
        r"\bbut\b",
        r"\bunless\b",
        r"\bonly if\b",
        r"\bdepends on\b",
        r"\bmay\b",
        r"\bcan\b",
        r"\brequires\b",
        r"\bcannot\b",
        r"\bdoes not\b",
    )
]
_STOPWORDS = {
    "a", "about", "after", "all", "also", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "between", "both", "but", "by", "can", "could",
    "did", "do", "does", "each", "for", "from", "had", "has", "have", "how", "if",
    "in", "into", "is", "it", "its", "may", "more", "most", "must", "no", "not",
    "of", "on", "only", "or", "other", "our", "out", "over", "same", "should", "so",
    "some", "such", "than", "that", "the", "their", "them", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "unless", "up", "use", "using",
    "very", "was", "we", "were", "what", "when", "which", "while", "with", "would",
}
_GENERIC_PHRASES = {
    "source file",
    "new york",
}


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _discover_source_paths(inputs: list[str | Path]) -> list[Path]:
    discovered: list[Path] = []
    seen: set[Path] = set()
    for item in inputs:
        path = Path(item)
        candidates: list[Path]
        if path.is_file():
            candidates = [path]
        elif (path / "documents").exists():
            candidates = sorted((path / "documents").glob("*/document.md"))
        elif path.is_dir():
            candidates = sorted(
                p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
            )
        else:
            candidates = []
        for candidate in candidates:
            if candidate.name in {"concept-alignment.yaml", "bundle.yaml", "bundle.yml"}:
                continue
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                discovered.append(candidate)
    return discovered


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _document_title(path: Path, text: str) -> str:
    match = _HEADING_RE.search(text)
    if match:
        return " ".join(match.group(1).split()).strip()
    return path.parent.name.replace("-", " ").strip() or path.stem.replace("-", " ").strip()


def _clean_sentence(text: str) -> str:
    text = _BULLET_RE.sub("", text)
    return " ".join(text.split()).strip(" -")


def _sentences(text: str) -> list[str]:
    return [cleaned for item in _SENTENCE_SPLIT_RE.split(text.replace("\n", " ")) if (cleaned := _clean_sentence(item))]


def _inventory_text_window(
    text: str,
    *,
    max_chars: int = 80000,
    max_sentences: int = 400,
) -> str:
    trimmed = text[:max_chars]
    sentences = _sentences(trimmed)
    if len(sentences) > max_sentences:
        sentences = sentences[:max_sentences]
    return " ".join(sentences)


def _extract_candidate_phrases(text: str, min_words: int = 2, max_words: int = 4) -> list[str]:
    tokens = _TOKEN_RE.findall(text)
    lowered = [token.lower() for token in tokens]
    out: list[str] = []
    seen: set[str] = set()
    for start in range(len(lowered)):
        for size in range(min_words, max_words + 1):
            window = lowered[start : start + size]
            if len(window) != size:
                continue
            if window[0] in _STOPWORDS or window[-1] in _STOPWORDS:
                continue
            if sum(1 for token in window if token in _STOPWORDS) > 1:
                continue
            if any(len(token) < 3 and token not in {"of", "vs"} for token in window):
                continue
            phrase = " ".join(window)
            if phrase in seen:
                continue
            seen.add(phrase)
            out.append(phrase)
    return out


def _score_phrase(entry: dict[str, Any], seed_slugs: set[str]) -> float:
    phrase_slug = _slugify(entry["phrase"])
    seed_bonus = 3 if phrase_slug in seed_slugs else 0
    prefix_bonus = 2 if any(phrase_slug in seed or seed in phrase_slug for seed in seed_slugs) else 0
    return (
        entry["document_count"] * 3
        + entry["occurrence_count"]
        + entry["definition_hits"] * 2
        + entry["distinction_hits"] * 2
        + entry["qualification_hits"]
        + entry["heading_hits"] * 2
        + seed_bonus
        + prefix_bonus
    )


def _is_redundant_subphrase(
    entry: dict[str, Any],
    group_rows: list[dict[str, Any]],
    seed_slugs: set[str],
) -> bool:
    phrase = str(entry["phrase"])
    phrase_slug = _slugify(phrase)
    if phrase_slug in seed_slugs:
        return False
    for other in group_rows:
        if other is entry:
            continue
        other_phrase = str(other["phrase"])
        if len(other_phrase) <= len(phrase):
            continue
        if not (other_phrase.startswith(f"{phrase} ") or other_phrase.endswith(f" {phrase}")):
            continue
        if (
            other["occurrence_count"] == entry["occurrence_count"]
            and other["document_count"] == entry["document_count"]
            and other["definition_hits"] >= entry["definition_hits"]
            and other["distinction_hits"] >= entry["distinction_hits"]
            and other["qualification_hits"] >= entry["qualification_hits"]
        ):
            return True
    return False


def _filter_phrase_rows(rows: list[dict[str, Any]], seed_slugs: set[str]) -> list[dict[str, Any]]:
    grouped: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["phrase"] in _GENERIC_PHRASES:
            continue
        grouped[(int(row["occurrence_count"]), int(row["document_count"]))].append(row)

    filtered: list[dict[str, Any]] = []
    for group in grouped.values():
        for row in group:
            if not _is_redundant_subphrase(row, group, seed_slugs):
                filtered.append(row)
    return filtered


def build_archive_phrase_inventory(
    inputs: list[str | Path],
    *,
    seed_terms: list[str] | None = None,
    top_n: int = 50,
) -> dict[str, Any]:
    paths = _discover_source_paths(inputs)
    seed_terms = [term.strip() for term in (seed_terms or []) if str(term).strip()]
    seed_slugs = {_slugify(term) for term in seed_terms}
    phrase_stats: dict[str, dict[str, Any]] = {}
    document_rows: list[dict[str, Any]] = []

    for path in paths:
        text = _read_text(path)
        title = _document_title(path, text)
        inventory_text = _inventory_text_window(text)
        heading_phrases = _extract_candidate_phrases(title, min_words=2, max_words=4)
        sentence_rows = _sentences(inventory_text)
        per_doc_counter: Counter[str] = Counter()
        per_doc_hits: defaultdict[str, dict[str, int]] = defaultdict(
            lambda: {"definition_hits": 0, "distinction_hits": 0, "qualification_hits": 0, "heading_hits": 0}
        )

        for phrase in heading_phrases:
            per_doc_counter[phrase] += 1
            per_doc_hits[phrase]["heading_hits"] += 1

        for sentence in sentence_rows:
            sentence_phrases = _extract_candidate_phrases(sentence)
            definition_hit = any(pattern.search(sentence) for pattern in _DEFINITION_PATTERNS)
            distinction_hit = any(pattern.search(sentence) for pattern in _DISTINCTION_PATTERNS)
            qualification_hit = any(pattern.search(sentence) for pattern in _QUALIFICATION_PATTERNS)
            for phrase in sentence_phrases:
                per_doc_counter[phrase] += 1
                if definition_hit:
                    per_doc_hits[phrase]["definition_hits"] += 1
                if distinction_hit:
                    per_doc_hits[phrase]["distinction_hits"] += 1
                if qualification_hit:
                    per_doc_hits[phrase]["qualification_hits"] += 1

        document_rows.append(
            {
                "path": str(path),
                "title": title,
                "top_phrases": [{"phrase": phrase, "count": count} for phrase, count in per_doc_counter.most_common(8)],
            }
        )

        for phrase, count in per_doc_counter.items():
            stats = phrase_stats.setdefault(
                phrase,
                {
                    "phrase": phrase,
                    "occurrence_count": 0,
                    "document_count": 0,
                    "definition_hits": 0,
                    "distinction_hits": 0,
                    "qualification_hits": 0,
                    "heading_hits": 0,
                    "source_paths": [],
                },
            )
            stats["occurrence_count"] += count
            stats["document_count"] += 1
            stats["definition_hits"] += per_doc_hits[phrase]["definition_hits"]
            stats["distinction_hits"] += per_doc_hits[phrase]["distinction_hits"]
            stats["qualification_hits"] += per_doc_hits[phrase]["qualification_hits"]
            stats["heading_hits"] += per_doc_hits[phrase]["heading_hits"]
            stats["source_paths"].append(str(path))

    phrase_rows = list(phrase_stats.values())
    for row in phrase_rows:
        row["seed_match"] = _slugify(row["phrase"]) in seed_slugs
        row["score"] = _score_phrase(row, seed_slugs)
        row["translation_priority"] = bool(
            row["seed_match"] or row["definition_hits"] or row["distinction_hits"] or row["qualification_hits"]
        )
        row["source_paths"] = sorted(set(row["source_paths"]))
    phrase_rows = _filter_phrase_rows(phrase_rows, seed_slugs)
    phrase_rows.sort(
        key=lambda item: (-float(item["score"]), -int(item["document_count"]), -int(item["occurrence_count"]), item["phrase"])
    )

    return {
        "summary": {
            "document_count": len(paths),
            "distinct_phrase_count": len(phrase_rows),
            "seed_term_count": len(seed_terms),
            "translation_priority_count": sum(1 for row in phrase_rows if row["translation_priority"]),
        },
        "input_paths": [str(Path(item)) for item in inputs],
        "seed_terms": seed_terms,
        "prioritized_concepts": [
            {
                "phrase": row["phrase"],
                "score": row["score"],
                "document_count": row["document_count"],
                "occurrence_count": row["occurrence_count"],
                "seed_match": row["seed_match"],
                "translation_priority": row["translation_priority"],
                "definition_hits": row["definition_hits"],
                "distinction_hits": row["distinction_hits"],
                "qualification_hits": row["qualification_hits"],
            }
            for row in phrase_rows[:top_n]
        ],
        "phrase_rows": phrase_rows[:top_n],
        "documents": document_rows,
    }


def write_archive_phrase_inventory_report(
    inputs: list[str | Path],
    out_path: str | Path,
    *,
    seed_terms: list[str] | None = None,
    top_n: int = 50,
) -> dict[str, Any]:
    report = build_archive_phrase_inventory(inputs, seed_terms=seed_terms, top_n=top_n)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path = out.with_suffix(".md")
    lines = [
        "# Archive Phrase Inventory",
        "",
        f"- documents: `{report['summary']['document_count']}`",
        f"- distinct phrases: `{report['summary']['distinct_phrase_count']}`",
        f"- seed terms: `{report['summary']['seed_term_count']}`",
        f"- translation-priority phrases: `{report['summary']['translation_priority_count']}`",
        "",
        "## Prioritized Concepts",
    ]
    for item in report["prioritized_concepts"][:20]:
        flags: list[str] = []
        if item["seed_match"]:
            flags.append("seed")
        if item["translation_priority"]:
            flags.append("translation")
        if item["distinction_hits"]:
            flags.append(f"distinctions={item['distinction_hits']}")
        if item["definition_hits"]:
            flags.append(f"definitions={item['definition_hits']}")
        if item["qualification_hits"]:
            flags.append(f"qualifications={item['qualification_hits']}")
        suffix = f" ({', '.join(flags)})" if flags else ""
        lines.append(f"- `{item['phrase']}` score={item['score']} docs={item['document_count']} hits={item['occurrence_count']}{suffix}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report_path": str(out), "markdown_path": str(md_path), "summary": report["summary"]}
