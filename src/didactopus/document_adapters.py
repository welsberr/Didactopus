from __future__ import annotations

import json
from pathlib import Path
import re
from .course_schema import NormalizedDocument, Section


def _title_from_path(path: str | Path) -> str:
    p = Path(path)
    return p.stem.replace("_", " ").replace("-", " ").title()


def _simple_section_split(text: str) -> list[Section]:
    sections = []
    current_heading = "Main"
    current_lines = []
    for line in text.splitlines():
        if re.match(r"^(#{1,3})\s+", line):
            if current_lines:
                sections.append(Section(heading=current_heading, body="\n".join(current_lines).strip()))
            current_heading = re.sub(r"^(#{1,3})\s+", "", line).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append(Section(heading=current_heading, body="\n".join(current_lines).strip()))
    return sections


def read_textish(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _safe_read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_bundle_path(base: Path, value: str | Path | None, fallback: Path) -> Path:
    if value is None or value == "":
        return fallback
    path = Path(value)
    if path.is_absolute():
        return path
    return base / path


def adapt_markdown(path: str | Path) -> NormalizedDocument:
    text = read_textish(path)
    return NormalizedDocument(
        source_path=str(path),
        source_type="markdown",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={},
    )


def adapt_text(path: str | Path) -> NormalizedDocument:
    text = read_textish(path)
    return NormalizedDocument(
        source_path=str(path),
        source_type="text",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={},
    )


def adapt_html(path: str | Path) -> NormalizedDocument:
    raw = read_textish(path)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return NormalizedDocument(
        source_path=str(path),
        source_type="html",
        title=_title_from_path(path),
        text=text,
        sections=[Section(heading="HTML Extract", body=text)],
        metadata={"extraction": "stub-html-strip"},
    )


def adapt_pdf(path: str | Path) -> NormalizedDocument:
    # Stub: in a real implementation, plug in PDF text extraction here.
    text = read_textish(path)
    return NormalizedDocument(
        source_path=str(path),
        source_type="pdf",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={"extraction": "stub-pdf-text"},
    )


def adapt_docx(path: str | Path) -> NormalizedDocument:
    # Stub: in a real implementation, plug in DOCX extraction here.
    text = read_textish(path)
    return NormalizedDocument(
        source_path=str(path),
        source_type="docx",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={"extraction": "stub-docx-text"},
    )


def adapt_pptx(path: str | Path) -> NormalizedDocument:
    # Stub: in a real implementation, plug in PPTX extraction here.
    text = read_textish(path)
    return NormalizedDocument(
        source_path=str(path),
        source_type="pptx",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={"extraction": "stub-pptx-text"},
    )


def is_doclift_bundle(path: str | Path) -> bool:
    base = Path(path)
    if not base.is_dir():
        return False
    manifest_path = base / "manifest.json"
    documents_dir = base / "documents"
    return manifest_path.exists() and documents_dir.exists()


def adapt_doclift_bundle(path: str | Path) -> list[NormalizedDocument]:
    base = Path(path)
    manifest = _safe_read_json(base / "manifest.json")
    by_output_dir = {
        Path(item.get("output_dir", "")).name: item
        for item in manifest.get("documents", [])
        if isinstance(item, dict) and item.get("output_dir")
    }
    docs: list[NormalizedDocument] = []
    for doc_dir in sorted(child for child in (base / "documents").iterdir() if child.is_dir()):
        markdown_path = doc_dir / "document.md"
        if not markdown_path.exists():
            continue
        text = markdown_path.read_text(encoding="utf-8")
        sections = _simple_section_split(text)
        bundle_meta = by_output_dir.get(doc_dir.name, {})
        layout_path = _resolve_bundle_path(base, bundle_meta.get("layout_path"), doc_dir / "document.layout.json")
        tables_path = _resolve_bundle_path(base, bundle_meta.get("tables_path"), doc_dir / "document.tables.json")
        figures_path = _resolve_bundle_path(base, bundle_meta.get("figures_path"), doc_dir / "document.figures.json")
        figures_payload = _safe_read_json(figures_path)
        tables_payload = _safe_read_json(tables_path)
        source_path = figures_payload.get("source_path") or tables_payload.get("source_path") or markdown_path.relative_to(base).as_posix()
        relative_doc_dir = doc_dir.relative_to(base).as_posix()
        relative_markdown_path = markdown_path.relative_to(base).as_posix()
        docs.append(
            NormalizedDocument(
                source_path=str(source_path),
                source_type="doclift_bundle",
                title=str(bundle_meta.get("title") or _title_from_path(doc_dir.name)),
                text=text,
                sections=sections,
                metadata={
                    "doclift_bundle": True,
                    "bundle_root": ".",
                    "bundle_document_dir": relative_doc_dir,
                    "bundle_markdown_path": relative_markdown_path,
                    "document_kind": bundle_meta.get("document_kind", "document"),
                    "source_path_kind": figures_payload.get("source_path_kind") or tables_payload.get("source_path_kind") or bundle_meta.get("source_path_kind", "source_root_relative"),
                    "layout_path": bundle_meta.get("layout_path", layout_path.relative_to(base).as_posix()),
                    "tables_path": bundle_meta.get("tables_path", tables_path.relative_to(base).as_posix()),
                    "figures_path": bundle_meta.get("figures_path", figures_path.relative_to(base).as_posix()),
                    "table_count": bundle_meta.get("table_count", 0),
                    "figure_reference_count": bundle_meta.get("figure_reference_count", 0),
                },
            )
        )
    return docs


def detect_adapter(path: str | Path) -> str:
    p = Path(path)
    if is_doclift_bundle(p):
        return "doclift_bundle"
    suffix = p.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix in {".txt"}:
        return "text"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix == ".pptx":
        return "pptx"
    return "text"


def is_supported_document(path: str | Path) -> bool:
    p = Path(path)
    return detect_adapter(p) in {"markdown", "text", "html", "pdf", "docx", "pptx", "doclift_bundle"} and (p.is_file() or p.is_dir())


def adapt_documents(path: str | Path) -> list[NormalizedDocument]:
    p = Path(path)
    if is_doclift_bundle(p):
        return adapt_doclift_bundle(p)
    if p.is_dir():
        docs = [adapt_document(child) for child in sorted(p.rglob("*")) if is_supported_document(child)]
        return docs
    return [adapt_document(p)]


def adapt_document(path: str | Path) -> NormalizedDocument:
    adapter = detect_adapter(path)
    if adapter == "doclift_bundle":
        docs = adapt_doclift_bundle(path)
        if not docs:
            raise ValueError(f"No documents found in doclift bundle {path}")
        return docs[0]
    if adapter == "markdown":
        return adapt_markdown(path)
    if adapter == "html":
        return adapt_html(path)
    if adapter == "pdf":
        return adapt_pdf(path)
    if adapter == "docx":
        return adapt_docx(path)
    if adapter == "pptx":
        return adapt_pptx(path)
    return adapt_text(path)
