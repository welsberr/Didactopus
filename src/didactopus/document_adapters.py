from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import tempfile
from .course_schema import NormalizedDocument, Section


def canonical_source_path(path: str | Path, display_root: str | Path | None = None) -> str:
    if display_root is None:
        return str(path)
    p = Path(path)
    root = Path(display_root)
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


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
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(path).read_text(encoding="latin-1")


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


def adapt_markdown(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    text = read_textish(path)
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
        source_type="markdown",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={},
    )


def adapt_text(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    text = read_textish(path)
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
        source_type="text",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={},
    )


def adapt_html(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    raw = read_textish(path)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
        source_type="html",
        title=_title_from_path(path),
        text=text,
        sections=[Section(heading="HTML Extract", body=text)],
        metadata={"extraction": "stub-html-strip"},
    )


def _extract_pdf_text(path: str | Path) -> tuple[str, str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    text = result.stdout
    if text.strip():
        return text, "pdftotext-layout"

    with tempfile.TemporaryDirectory(prefix="didactopus-pdf-ocr-") as tmp:
        tmp_path = Path(tmp)
        sidecar = tmp_path / "sidecar.txt"
        output_pdf = tmp_path / "ocr.pdf"
        subprocess.run(
            ["ocrmypdf", "--sidecar", str(sidecar), str(path), str(output_pdf)],
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if sidecar.exists():
            text = sidecar.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        raise RuntimeError(f"PDF text extraction produced no text: {path}")
    return text, "ocrmypdf-sidecar"


def adapt_pdf(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    text, extraction = _extract_pdf_text(path)
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
        source_type="pdf",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={"extraction": extraction},
    )


def adapt_docx(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    # Stub: in a real implementation, plug in DOCX extraction here.
    text = read_textish(path)
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
        source_type="docx",
        title=_title_from_path(path),
        text=text,
        sections=_simple_section_split(text),
        metadata={"extraction": "stub-docx-text"},
    )


def adapt_pptx(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    # Stub: in a real implementation, plug in PPTX extraction here.
    text = read_textish(path)
    return NormalizedDocument(
        source_path=canonical_source_path(path, display_root),
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
    return (base / "manifest.json").exists() and (base / "documents").exists()


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
        bundle_meta = by_output_dir.get(doc_dir.name, {})
        layout_path = _resolve_bundle_path(base, bundle_meta.get("layout_path"), doc_dir / "document.layout.json")
        tables_path = _resolve_bundle_path(base, bundle_meta.get("tables_path"), doc_dir / "document.tables.json")
        figures_path = _resolve_bundle_path(base, bundle_meta.get("figures_path"), doc_dir / "document.figures.json")
        figures_payload = _safe_read_json(figures_path)
        tables_payload = _safe_read_json(tables_path)
        source_path = figures_payload.get("source_path") or tables_payload.get("source_path") or markdown_path.relative_to(base).as_posix()
        docs.append(
            NormalizedDocument(
                source_path=str(source_path),
                source_type="doclift_bundle",
                title=str(bundle_meta.get("title") or _title_from_path(doc_dir.name)),
                text=text,
                sections=_simple_section_split(text),
                metadata={
                    "doclift_bundle": True,
                    "bundle_root": ".",
                    "bundle_document_dir": doc_dir.relative_to(base).as_posix(),
                    "bundle_markdown_path": markdown_path.relative_to(base).as_posix(),
                    "document_kind": bundle_meta.get("document_kind", "document"),
                    "source_path_kind": figures_payload.get("source_path_kind")
                    or tables_payload.get("source_path_kind")
                    or bundle_meta.get("source_path_kind", "source_root_relative"),
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
    if p.is_dir():
        return is_doclift_bundle(p)
    return p.is_file() and detect_adapter(p) in {"markdown", "text", "html", "pdf", "docx", "pptx"}


def adapt_documents(path: str | Path, display_root: str | Path | None = None) -> list[NormalizedDocument]:
    p = Path(path)
    if is_doclift_bundle(p):
        return adapt_doclift_bundle(p)
    if p.is_dir():
        docs = [adapt_document(child, display_root=display_root) for child in sorted(p.rglob("*")) if is_supported_document(child)]
        return docs
    return [adapt_document(p, display_root=display_root)]


def adapt_document(path: str | Path, display_root: str | Path | None = None) -> NormalizedDocument:
    adapter = detect_adapter(path)
    if adapter == "doclift_bundle":
        docs = adapt_doclift_bundle(path)
        if not docs:
            raise ValueError(f"Doclift bundle contains no adaptable documents: {path}")
        return docs[0]
    if adapter == "markdown":
        return adapt_markdown(path, display_root=display_root)
    if adapter == "html":
        return adapt_html(path, display_root=display_root)
    if adapter == "pdf":
        return adapt_pdf(path, display_root=display_root)
    if adapter == "docx":
        return adapt_docx(path, display_root=display_root)
    if adapter == "pptx":
        return adapt_pptx(path, display_root=display_root)
    return adapt_text(path, display_root=display_root)
