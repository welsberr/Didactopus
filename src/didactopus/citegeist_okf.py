from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_citegeist_okf_bundle(bundle_dir: str | Path) -> dict[str, Any]:
    base = Path(bundle_dir)
    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("bundle_kind") != "citegeist_okf_bundle":
        raise ValueError(f"Not a CiteGeist OKF bundle: {bundle_dir}")

    works = []
    for citation_key, relative_path in sorted((manifest.get("paths", {}).get("works") or {}).items()):
        path = base / relative_path
        if not path.exists():
            continue
        frontmatter, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        works.append(
            {
                "citation_key": citation_key,
                "path": relative_path,
                "title": frontmatter.get("title") or citation_key,
                "entry_type": frontmatter.get("entry_type", "work"),
                "review_status": frontmatter.get("review_status", ""),
                "year": frontmatter.get("year", ""),
                "doi": frontmatter.get("doi", ""),
                "url": frontmatter.get("url", ""),
                "authors": frontmatter.get("authors", []),
                "topic_slugs": frontmatter.get("topic_slugs", []),
                "abstract": _extract_section(body, "Abstract"),
                "citation_targets": _extract_citation_targets(body),
            }
        )

    return {
        "bundle_kind": "didactopus_citegeist_okf_source_bundle",
        "source_bundle": manifest,
        "works": works,
    }


def build_source_corpus_from_citegeist_okf(bundle_dir: str | Path) -> dict[str, Any]:
    bundle = load_citegeist_okf_bundle(bundle_dir)
    source_manifest = bundle["source_bundle"]
    works = bundle["works"]
    return {
        "course_title": (source_manifest.get("topic") or {}).get("name") or "CiteGeist Literature Bundle",
        "rights_note": "Bibliographic metadata imported from a CiteGeist OKF bundle; review source licenses before redistribution.",
        "sources": [
            {
                "source_path": work["path"],
                "source_type": "citegeist_okf_work",
                "title": work["title"],
                "metadata": {
                    "citation_key": work["citation_key"],
                    "entry_type": work["entry_type"],
                    "review_status": work["review_status"],
                    "year": work["year"],
                    "doi": work["doi"],
                    "url": work["url"],
                    "authors": work["authors"],
                    "topic_slugs": work["topic_slugs"],
                    "citation_targets": work["citation_targets"],
                },
            }
            for work in works
        ],
        "fragments": _build_fragments(works),
    }


def write_citegeist_okf_source_bundle(bundle_dir: str | Path, out_dir: str | Path) -> dict[str, str]:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    source_corpus = build_source_corpus_from_citegeist_okf(bundle_dir)
    resources_md = _render_resources(source_corpus)
    source_corpus_path = target / "source_corpus.json"
    resources_path = target / "resources.md"
    manifest_path = target / "citegeist_okf_import_manifest.json"
    source_corpus_path.write_text(json.dumps(source_corpus, indent=2), encoding="utf-8")
    resources_path.write_text(resources_md, encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "bundle_kind": "didactopus_citegeist_okf_source_bundle",
                "source_corpus": source_corpus_path.name,
                "resources": resources_path.name,
                "source_count": len(source_corpus["sources"]),
                "fragment_count": len(source_corpus["fragments"]),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "source_corpus_path": str(source_corpus_path),
        "resources_path": str(resources_path),
        "manifest_path": str(manifest_path),
    }


def _build_fragments(works: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fragments: list[dict[str, Any]] = []
    for work in works:
        citation_key = str(work["citation_key"])
        fragments.append(
            {
                "fragment_id": f"citegeist::{_safe_id(citation_key)}::bibliographic-summary",
                "kind": "bibliographic_summary",
                "module_title": "Literature",
                "lesson_title": str(work["title"]),
                "text": _summary_text(work),
                "source_refs": [citation_key],
                "objectives": [],
                "exercises": [],
                "key_terms": list(work.get("topic_slugs") or []),
            }
        )
        if work.get("abstract"):
            fragments.append(
                {
                    "fragment_id": f"citegeist::{_safe_id(citation_key)}::abstract",
                    "kind": "abstract",
                    "module_title": "Literature",
                    "lesson_title": str(work["title"]),
                    "text": str(work["abstract"]),
                    "source_refs": [citation_key],
                    "objectives": [],
                    "exercises": [],
                    "key_terms": list(work.get("topic_slugs") or []),
                }
            )
    return fragments


def _summary_text(work: dict[str, Any]) -> str:
    title = str(work.get("title") or work["citation_key"])
    entry_type = str(work.get("entry_type") or "work")
    year = str(work.get("year") or "").strip()
    authors = work.get("authors") or []
    author_text = ", ".join(str(author) for author in authors[:3]) if isinstance(authors, list) else str(authors)
    parts = [f"{title} is a CiteGeist {entry_type}"]
    if author_text:
        parts.append(f"by {author_text}")
    if year:
        parts.append(f"from {year}")
    text = " ".join(parts) + "."
    if work.get("doi"):
        text += f" DOI: {work['doi']}."
    return text


def _render_resources(source_corpus: dict[str, Any]) -> str:
    lines = ["# CiteGeist Literature Resources", ""]
    for source in source_corpus["sources"]:
        metadata = source["metadata"]
        line = f"- `{metadata['citation_key']}`: {source['title']}"
        if metadata.get("year"):
            line += f" ({metadata['year']})"
        if metadata.get("doi"):
            line += f" DOI: {metadata['doi']}"
        lines.append(line)
    lines.append("")
    return "\n".join(lines)


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    frontmatter: dict[str, Any] = {}
    key = ""
    for raw_line in text[4:end].splitlines():
        if raw_line.startswith("  - ") and key:
            frontmatter.setdefault(key, []).append(_clean_scalar(raw_line[4:]))
            continue
        if ":" in raw_line:
            key, value = raw_line.split(":", 1)
            key = key.strip()
            value = value.strip()
            frontmatter[key] = [] if value == "" else _clean_scalar(value)
    return frontmatter, text[end + 4 :].lstrip()


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def _extract_section(body: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(body)
    if not match:
        return ""
    rest = body[match.end() :].strip()
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: next_heading.start()].strip() if next_heading else rest
    return re.sub(r"\s+", " ", section).strip()


def _extract_citation_targets(body: str) -> list[str]:
    section = _extract_section(body, "Citation Graph")
    return re.findall(r"^-\s+\[([^\]]+)\]\([^)]+\)", section, flags=re.MULTILINE)


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"
