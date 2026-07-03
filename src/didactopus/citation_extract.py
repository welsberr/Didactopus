from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


YEAR_RE = r"(?:1[6-9]\d{2}|20\d{2}|21\d{2})[a-z]?"
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
REFERENCE_HEADING_PATTERN = re.compile(
    r"^\s*(?:references|bibliography|literature cited|works cited|selected references|selected bibliography)\s*$",
    re.IGNORECASE,
)
REFERENCE_END_HEADING_PATTERN = re.compile(
    r"^\s*(?:index|appendix|appendices|acknowledg(?:e)?ments|notes)\s*$",
    re.IGNORECASE,
)
REFERENCE_START_PATTERN = re.compile(
    rf"^\s*(?:\[\d+\]|\d+[.)])?\s*"
    rf"(?:[A-Z][A-Za-z'`-]+|[A-Z][A-Za-z'`-]+\s+and\s+[A-Z][A-Za-z'`-]+|[A-Z][A-Za-z'`-]+\s*&\s*[A-Z][A-Za-z'`-]+)"
    rf"(?:,\s*[A-Z][A-Za-z'`-]+|,\s*[A-Z]\.|(?:\s+[A-Z]\.){{0,4}}|(?:\s+et\s+al\.?)?)"
    rf".{{0,160}}\b{YEAR_RE}\b",
    re.IGNORECASE,
)
PAREN_CITATION_PATTERN = re.compile(
    rf"\((?P<citation>"
    rf"(?:see\s+|cf\.\s+|e\.g\.\s+)?"
    rf"[A-Z][A-Za-z'`-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'`-]+|\s+et\s+al\.?)?"
    rf"[^()]*?\b{YEAR_RE}\b[^()]{{0,120}}"
    rf")\)"
)
NARRATIVE_CITATION_PATTERN = re.compile(
    rf"\b(?P<author>[A-Z][A-Za-z'`-]+(?:\s+et\s+al\.?)?)\s+\((?P<year>{YEAR_RE})\)"
)


@dataclass(slots=True)
class CitationExtractionResult:
    out_dir: Path
    manifest: dict[str, Any]
    artifacts: dict[str, str]


def run_citations_from_ingest(
    ingest_dir: str | Path,
    out_dir: str | Path | None = None,
    *,
    run_id: str | None = None,
    citegeist_src: str | Path | None = None,
    citegeist_backend: str = "heuristic",
    use_citegeist: bool = True,
    max_fragments: int | None = None,
) -> CitationExtractionResult:
    source_root = Path(ingest_dir)
    if not source_root.exists():
        raise FileNotFoundError(f"Ingest directory does not exist: {ingest_dir}")
    runs = _discover_ingest_runs(source_root)
    if not runs:
        raise ValueError(f"No ensemble ingestion artifacts found under: {ingest_dir}")

    target = Path(out_dir) if out_dir is not None else source_root / "citation-extraction"
    target.mkdir(parents=True, exist_ok=True)
    actual_run_id = run_id or f"citation-pass-{_utc_compact_timestamp()}"

    source_rows_by_run: dict[str, dict[str, dict[str, Any]]] = {}
    reference_candidates: list[dict[str, Any]] = []
    in_text_citations: list[dict[str, Any]] = []
    citation_links: list[dict[str, Any]] = []
    processed_fragment_count = 0
    processed_run_count = 0
    errors: list[dict[str, str]] = []

    for run_path in runs:
        run_label = run_path.name
        try:
            manifest = json.loads((run_path / "manifest.json").read_text(encoding="utf-8"))
            sources = _read_jsonl(run_path / "sources.jsonl")
            fragments = _read_jsonl(run_path / "fragments.jsonl")
        except Exception as exc:  # noqa: BLE001 - citation pass should report run-level failures.
            errors.append({"run_path": str(run_path), "error": str(exc)})
            continue

        processed_run_count += 1
        source_rows = {str(row["source_id"]): row for row in sources}
        source_rows_by_run[run_label] = source_rows
        for fragment in fragments:
            if max_fragments is not None and processed_fragment_count >= max_fragments:
                break
            processed_fragment_count += 1
            source_row = source_rows.get(str(fragment.get("source_id")), {})
            run_context = {
                "ingest_run_path": str(run_path),
                "ingest_id": str(manifest.get("ingest_id") or run_label),
                "source_id": str(fragment.get("source_id") or ""),
                "source_path": str(fragment.get("source_path") or source_row.get("path") or ""),
                "fragment_id": str(fragment.get("fragment_id") or ""),
                "section": str(fragment.get("section") or ""),
            }
            ref_rows, ref_links = _extract_reference_candidates(fragment, run_context)
            citation_rows, citation_occurrences = _extract_in_text_citations(fragment, run_context)
            reference_candidates.extend(ref_rows)
            in_text_citations.extend(citation_rows)
            citation_links.extend(ref_links)
            citation_links.extend(citation_occurrences)

    reference_candidates = _dedupe_candidates(reference_candidates, "reference_key")
    in_text_citations = _dedupe_candidates(in_text_citations, "citation_key")
    citation_links = _dedupe_candidates(citation_links, "occurrence_key")

    reference_text = "\n\n".join(row["text"] for row in reference_candidates)
    reference_text_path = target / "reference_candidates.txt"
    reference_text_path.write_text(reference_text + ("\n" if reference_text else ""), encoding="utf-8")

    citegeist_payload = _run_citegeist_extraction(
        reference_text,
        target,
        citegeist_src=citegeist_src,
        backend=citegeist_backend,
        enabled=use_citegeist,
    )

    _write_jsonl(target / "reference_candidates.jsonl", reference_candidates)
    _write_jsonl(target / "in_text_citations.jsonl", in_text_citations)
    _write_jsonl(target / "citation_links.jsonl", citation_links)

    manifest = {
        "run_kind": "didactopus_citations_from_ingest",
        "run_id": actual_run_id,
        "source_ingest_root": str(source_root),
        "source_ingest_runs": [str(path) for path in runs],
        "created_at": _utc_timestamp(),
        "processed_run_count": processed_run_count,
        "processed_fragment_count": processed_fragment_count,
        "counts": {
            "reference_candidate_count": len(reference_candidates),
            "in_text_citation_count": len(in_text_citations),
            "citation_link_count": len(citation_links),
            "citegeist_entry_count": citegeist_payload.get("entry_count", 0),
            "error_count": len(errors),
        },
        "citegeist": citegeist_payload,
        "errors": errors,
        "artifacts": {
            "reference_candidates": "reference_candidates.jsonl",
            "reference_text": "reference_candidates.txt",
            "in_text_citations": "in_text_citations.jsonl",
            "citation_links": "citation_links.jsonl",
            "citegeist_bibtex": "citegeist_extracted.bib",
            "citegeist_entries": "citegeist_extracted.json",
        },
        "review_policy": "All citation links and CiteGeist outputs are draft until source identity and support relation are reviewed.",
    }
    _write_json(target / "citation_link_manifest.json", manifest)
    artifacts = {key: str(target / value) for key, value in manifest["artifacts"].items()}
    artifacts["manifest"] = str(target / "citation_link_manifest.json")
    return CitationExtractionResult(out_dir=target, manifest=manifest, artifacts=artifacts)


def _discover_ingest_runs(root: Path) -> list[Path]:
    if (root / "manifest.json").exists() and (root / "fragments.jsonl").exists():
        return [root]
    runs = []
    for manifest in sorted(root.glob("**/manifest.json")):
        run_dir = manifest.parent
        if (run_dir / "fragments.jsonl").exists() and (run_dir / "sources.jsonl").exists():
            if "citation-extraction" not in run_dir.parts:
                runs.append(run_dir)
    return runs


def _extract_reference_candidates(fragment: dict[str, Any], context: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = str(fragment.get("text") or "")
    explicit = _has_reference_heading(str(fragment.get("section") or "")) or _has_reference_heading(text)
    blocks = _reference_blocks(text, explicit=explicit)
    rows = []
    links = []
    for index, block in enumerate(blocks, start=1):
        reference_key = _stable_key("reference", block)
        row = {
            "reference_candidate_id": f"refcand_{reference_key[:16]}",
            "reference_key": reference_key,
            "text": block,
            "normalized_text": _normalize_candidate_text(block),
            "source_id": context["source_id"],
            "source_path": context["source_path"],
            "fragment_id": context["fragment_id"],
            "section": context["section"],
            "ingest_id": context["ingest_id"],
            "confidence_hint": 0.82 if explicit else 0.68,
            "finding_codes": ["reference_section_candidate"] if explicit else ["reference_line_candidate"],
            "current_status": "draft",
        }
        occurrence_key = _stable_key("reference-occurrence", context["fragment_id"], str(index), block)
        link = {
            "citation_occurrence_id": f"citeocc_{occurrence_key[:16]}",
            "occurrence_key": occurrence_key,
            "candidate_type": "reference_entry",
            "candidate_key": reference_key,
            "text": block,
            "source_id": context["source_id"],
            "source_path": context["source_path"],
            "fragment_id": context["fragment_id"],
            "section": context["section"],
            "ingest_id": context["ingest_id"],
            "confidence_hint": row["confidence_hint"],
            "current_status": "draft",
        }
        rows.append(row)
        links.append(link)
    return rows, links


def _extract_in_text_citations(fragment: dict[str, Any], context: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = str(fragment.get("text") or "")
    rows: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    for match in PAREN_CITATION_PATTERN.finditer(text):
        citation_text = match.group("citation").strip()
        if _reject_parenthetical_citation(citation_text):
            continue
        rows.append(_citation_candidate_row(citation_text, "author_year_parenthetical", context, match.start(), match.end()))
        occurrences.append(_citation_occurrence_row(citation_text, "in_text_citation", context, match.start(), match.end(), 0.64))
    for match in NARRATIVE_CITATION_PATTERN.finditer(text):
        citation_text = f"{match.group('author')} {match.group('year')}"
        rows.append(_citation_candidate_row(citation_text, "author_year_narrative", context, match.start(), match.end()))
        occurrences.append(_citation_occurrence_row(citation_text, "in_text_citation", context, match.start(), match.end(), 0.62))
    for match in DOI_PATTERN.finditer(text):
        doi_text = match.group(0).rstrip(".,;)")
        rows.append(_citation_candidate_row(doi_text, "doi", context, match.start(), match.end(), confidence=0.86))
        occurrences.append(_citation_occurrence_row(doi_text, "doi", context, match.start(), match.end(), 0.86))
    return rows, occurrences


def _citation_candidate_row(
    citation_text: str,
    citation_kind: str,
    context: dict[str, str],
    start: int,
    end: int,
    *,
    confidence: float = 0.64,
) -> dict[str, Any]:
    citation_key = _stable_key(citation_kind, _normalize_candidate_text(citation_text))
    return {
        "citation_candidate_id": f"citecand_{citation_key[:16]}",
        "citation_key": citation_key,
        "citation_kind": citation_kind,
        "text": citation_text,
        "normalized_text": _normalize_candidate_text(citation_text),
        "source_id": context["source_id"],
        "source_path": context["source_path"],
        "fragment_id": context["fragment_id"],
        "section": context["section"],
        "ingest_id": context["ingest_id"],
        "char_start": start,
        "char_end": end,
        "confidence_hint": confidence,
        "current_status": "draft",
    }


def _citation_occurrence_row(
    citation_text: str,
    candidate_type: str,
    context: dict[str, str],
    start: int,
    end: int,
    confidence: float,
) -> dict[str, Any]:
    occurrence_key = _stable_key(candidate_type, context["fragment_id"], str(start), str(end), citation_text)
    candidate_key = _stable_key("doi" if candidate_type == "doi" else "author_year_parenthetical", _normalize_candidate_text(citation_text))
    return {
        "citation_occurrence_id": f"citeocc_{occurrence_key[:16]}",
        "occurrence_key": occurrence_key,
        "candidate_type": candidate_type,
        "candidate_key": candidate_key,
        "text": citation_text,
        "source_id": context["source_id"],
        "source_path": context["source_path"],
        "fragment_id": context["fragment_id"],
        "section": context["section"],
        "ingest_id": context["ingest_id"],
        "char_start": start,
        "char_end": end,
        "confidence_hint": confidence,
        "current_status": "draft",
    }


def _reference_blocks(text: str, *, explicit: bool) -> list[str]:
    all_lines = text.splitlines()
    if not explicit and not _has_reference_density(all_lines):
        return []
    lines = _reference_region_lines(text, explicit=explicit)
    blocks: list[str] = []
    current: list[str] = []
    for raw_line in lines:
        line = " ".join(raw_line.strip().split())
        if len(line) < 18:
            continue
        starts_new = _looks_like_reference_start(line)
        if starts_new and current:
            blocks.append(" ".join(current).strip())
            current = [line]
            continue
        if starts_new or current or explicit:
            current.append(line)
    if current:
        blocks.append(" ".join(current).strip())
    return [_clean_reference_block(block) for block in blocks if _looks_like_reference_block(block)]


def _reference_region_lines(text: str, *, explicit: bool) -> list[str]:
    lines = text.splitlines()
    if not explicit:
        return [line for line in lines if _looks_like_reference_start(line) or DOI_PATTERN.search(line)]
    selected: list[str] = []
    active = False
    for line in lines:
        if REFERENCE_HEADING_PATTERN.match(line):
            active = True
            continue
        if active and REFERENCE_END_HEADING_PATTERN.match(line):
            break
        if active:
            selected.append(line)
    return selected if selected else lines


def _has_reference_heading(text: str) -> bool:
    if REFERENCE_HEADING_PATTERN.match(text.strip()):
        return True
    return any(REFERENCE_HEADING_PATTERN.match(line) for line in text.splitlines())


def _has_reference_density(lines: list[str]) -> bool:
    meaningful = [line for line in lines if len(line.strip()) >= 18]
    if len(meaningful) < 2:
        return False
    reference_like = sum(1 for line in meaningful if _looks_like_reference_start(line) or DOI_PATTERN.search(line))
    return reference_like >= 2 and reference_like / len(meaningful) >= 0.45


def _looks_like_reference_start(line: str) -> bool:
    stripped = line.strip()
    if DOI_PATTERN.search(stripped):
        return True
    if stripped.casefold().startswith(("copyright", "all rights reserved", "printed in")):
        return False
    year_match = re.search(rf"\b{YEAR_RE}\b", stripped)
    if year_match is None:
        return False
    if not REFERENCE_START_PATTERN.match(stripped):
        return False
    prefix = stripped[: year_match.start()]
    if len(prefix) > 140:
        return False
    if re.match(r"^\s*(?:\[\d+\]|\d+[.)])", stripped):
        return True
    if "," in prefix and (re.search(r"\b[A-Z]\.", prefix) or re.search(r"\b[A-Z][a-z]{2,},", prefix)):
        return True
    if re.search(r"\bet\s+al\.?", prefix, re.IGNORECASE):
        return True
    return False


def _looks_like_reference_block(block: str) -> bool:
    if len(block) < 35:
        return False
    if DOI_PATTERN.search(block):
        return True
    return bool(re.search(rf"\b{YEAR_RE}\b", block)) and bool(re.search(r"[A-Za-z]{3,}", block))


def _clean_reference_block(block: str) -> str:
    return re.sub(r"\s+", " ", block).strip(" \t\r\n-")


def _reject_parenthetical_citation(citation_text: str) -> bool:
    lowered = citation_text.casefold()
    if len(citation_text) > 180:
        return True
    if lowered.startswith(("fig", "figure", "table", "chapter", "page", "pp.", "eq.", "equation")):
        return True
    if not re.search(rf"\b{YEAR_RE}\b", citation_text):
        return True
    return False


def _run_citegeist_extraction(
    reference_text: str,
    out_dir: Path,
    *,
    citegeist_src: str | Path | None,
    backend: str,
    enabled: bool,
) -> dict[str, Any]:
    bib_path = out_dir / "citegeist_extracted.bib"
    entries_path = out_dir / "citegeist_extracted.json"
    if not enabled:
        bib_path.write_text("", encoding="utf-8")
        entries_path.write_text("[]\n", encoding="utf-8")
        return {"enabled": False, "status": "skipped", "entry_count": 0, "backend": backend}
    if not reference_text.strip():
        bib_path.write_text("", encoding="utf-8")
        entries_path.write_text("[]\n", encoding="utf-8")
        return {"enabled": True, "status": "no_reference_candidates", "entry_count": 0, "backend": backend}
    source_path = _resolve_citegeist_src(citegeist_src)
    if source_path is None:
        bib_path.write_text("", encoding="utf-8")
        entries_path.write_text("[]\n", encoding="utf-8")
        return {"enabled": True, "status": "citegeist_not_found", "entry_count": 0, "backend": backend}
    inserted = False
    source_path_text = str(source_path)
    if source_path_text not in sys.path:
        sys.path.insert(0, source_path_text)
        inserted = True
    try:
        extract_mod = importlib.import_module("citegeist.extract")
        bibtex_mod = importlib.import_module("citegeist.bibtex")
        entries = extract_mod.extract_references(reference_text, backend=backend)
        rendered = bibtex_mod.render_bibtex(entries)
        bib_path.write_text(rendered + ("\n" if rendered else ""), encoding="utf-8")
        payload = [
            {
                "citation_key": entry.citation_key,
                "entry_type": entry.entry_type,
                "fields": dict(entry.fields),
            }
            for entry in entries
        ]
        entries_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return {
            "enabled": True,
            "status": "ok",
            "entry_count": len(entries),
            "backend": backend,
            "citegeist_src": source_path_text,
        }
    except Exception as exc:  # noqa: BLE001 - citegeist is an optional integration.
        fallback = _run_citegeist_subprocess(reference_text, out_dir, source_path, backend)
        if fallback is not None:
            return fallback | {
                "enabled": True,
                "backend": backend,
                "citegeist_src": source_path_text,
                "direct_import_error": str(exc),
            }
        bib_path.write_text("", encoding="utf-8")
        entries_path.write_text("[]\n", encoding="utf-8")
        return {
            "enabled": True,
            "status": "error",
            "entry_count": 0,
            "backend": backend,
            "citegeist_src": source_path_text,
            "error": str(exc),
        }
    finally:
        if inserted:
            try:
                sys.path.remove(source_path_text)
            except ValueError:
                pass


def _resolve_citegeist_src(citegeist_src: str | Path | None) -> Path | None:
    candidates = []
    if citegeist_src is not None:
        candidates.append(Path(citegeist_src))
    env_src = os.environ.get("CITEGEIST_SRC")
    if env_src:
        candidates.append(Path(env_src))
    repo_root = Path(__file__).resolve().parents[3]
    candidates.extend([repo_root.parent / "CiteGeist" / "src", repo_root.parent / "CiteGeist"])
    for candidate in candidates:
        if (candidate / "citegeist" / "extract.py").exists():
            return candidate
    return None


def _run_citegeist_subprocess(reference_text: str, out_dir: Path, source_path: Path, backend: str) -> dict[str, Any] | None:
    python_path = _resolve_citegeist_python(source_path)
    if python_path is None:
        return None

    reference_text_path = out_dir / "reference_candidates.txt"
    bib_path = out_dir / "citegeist_extracted.bib"
    entries_path = out_dir / "citegeist_extracted.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source_path) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    extract_code = """
from pathlib import Path
import json
import sys
from citegeist.extract import extract_references
from citegeist.bibtex import render_bibtex

input_path = Path(sys.argv[1])
backend = sys.argv[2]
bib_path = Path(sys.argv[3])
entries_path = Path(sys.argv[4])
entries = extract_references(input_path.read_text(encoding="utf-8"), backend=backend)
records = []
bib_blocks = []
for entry in entries:
    record = {
        "citation_key": entry.citation_key,
        "entry_type": entry.entry_type,
        "fields": dict(entry.fields),
    }
    try:
        rendered = render_bibtex([entry]).strip()
        if rendered:
            bib_blocks.append(rendered)
        record["render_status"] = "ok"
    except Exception as exc:  # keep malformed draft references reviewable.
        record["render_status"] = "render_error"
        record["render_error"] = str(exc)
    records.append(record)
bib_path.write_text("\\n\\n".join(bib_blocks) + ("\\n" if bib_blocks else ""), encoding="utf-8")
entries_path.write_text(json.dumps(records, indent=2) + "\\n", encoding="utf-8")
print(json.dumps({
    "entry_count": len(records),
    "rendered_entry_count": len(bib_blocks),
    "render_error_count": sum(1 for record in records if record.get("render_status") != "ok"),
}))
""".strip()
    extract_result = subprocess.run(
        [str(python_path), "-c", extract_code, str(reference_text_path), backend, str(bib_path), str(entries_path)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if extract_result.returncode != 0:
        bib_path.write_text("", encoding="utf-8")
        entries_path.write_text("[]\n", encoding="utf-8")
        return {
            "status": "subprocess_error",
            "entry_count": 0,
            "citegeist_python": str(python_path),
            "error": (extract_result.stderr or extract_result.stdout).strip(),
        }

    try:
        summary = json.loads(extract_result.stdout or "{}")
    except json.JSONDecodeError:
        summary = {}
    payload: dict[str, Any] = {
        "status": "ok",
        "entry_count": int(summary.get("entry_count") or 0),
        "rendered_entry_count": int(summary.get("rendered_entry_count") or _count_bibtex_entries(bib_path.read_text(encoding="utf-8") if bib_path.exists() else "")),
        "render_error_count": int(summary.get("render_error_count") or 0),
        "citegeist_python": str(python_path),
    }
    return payload


def _resolve_citegeist_python(source_path: Path) -> Path | None:
    repo_root = source_path.parent
    candidates = [
        repo_root / ".venv" / "bin" / "python",
        repo_root / ".venv" / "bin" / "python3",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _count_bibtex_entries(text: str) -> int:
    return len(re.findall(r"(?m)^@\w+\s*\{", text))


def _dedupe_candidates(rows: list[dict[str, Any]], key_name: str) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get(key_name) or _stable_key(json.dumps(row, sort_keys=True)))
        if key not in seen:
            seen[key] = row
    return list(seen.values())


def _normalize_candidate_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _stable_key(*parts: str) -> str:
    digest = hashlib.sha1()
    for part in parts:
        digest.update(part.encode("utf-8", errors="replace"))
        digest.update(b"\0")
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
