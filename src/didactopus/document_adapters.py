from __future__ import annotations

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


def detect_adapter(path: str | Path) -> str:
    p = Path(path)
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


def adapt_document(path: str | Path) -> NormalizedDocument:
    adapter = detect_adapter(path)
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
