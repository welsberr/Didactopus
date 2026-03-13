from pathlib import Path
from didactopus.document_adapters import adapt_document, detect_adapter


def test_detect_adapter() -> None:
    assert detect_adapter("a.md") == "markdown"
    assert detect_adapter("b.html") == "html"
    assert detect_adapter("c.pdf") == "pdf"
    assert detect_adapter("d.docx") == "docx"
    assert detect_adapter("e.pptx") == "pptx"


def test_adapt_markdown(tmp_path: Path) -> None:
    p = tmp_path / "x.md"
    p.write_text("# T\n\n## A\nBody", encoding="utf-8")
    doc = adapt_document(p)
    assert doc.source_type == "markdown"
    assert len(doc.sections) >= 1
