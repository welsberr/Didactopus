from pathlib import Path
import subprocess
from didactopus.document_adapters import adapt_document, adapt_documents, canonical_source_path, detect_adapter


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


def test_adapt_text_falls_back_to_latin1(tmp_path: Path) -> None:
    p = tmp_path / "legacy.txt"
    p.write_bytes("Darwin\u2019s text".encode("windows-1252"))

    doc = adapt_document(p)

    assert doc.source_type == "text"
    assert "Darwin" in doc.text


def test_canonical_source_path_uses_display_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    src = root / "course" / "unit.md"
    src.parent.mkdir(parents=True)
    src.write_text("# T\n\nBody", encoding="utf-8")

    assert canonical_source_path(src, root) == "course/unit.md"


def test_adapt_documents_applies_display_root_to_tree(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "course" / "nested").mkdir(parents=True)
    (root / "course" / "unit1.md").write_text("# T\n\n## A\nBody", encoding="utf-8")
    (root / "course" / "nested" / "unit2.txt").write_text("## B\nBody", encoding="utf-8")

    docs = adapt_documents(root / "course", display_root=root)

    assert [doc.source_path for doc in docs] == ["course/nested/unit2.txt", "course/unit1.md"]


def test_adapt_pdf_uses_pdftotext(tmp_path: Path, monkeypatch) -> None:
    pdf = tmp_path / "example.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="# Extracted\n\nBody")

    monkeypatch.setattr(subprocess, "run", fake_run)

    doc = adapt_document(pdf, display_root=tmp_path)

    assert doc.source_type == "pdf"
    assert doc.source_path == "example.pdf"
    assert doc.metadata["extraction"] == "pdftotext-layout"
    assert doc.text == "# Extracted\n\nBody"
    assert calls[0][0] == ["pdftotext", "-layout", str(pdf), "-"]


def test_adapt_pdf_falls_back_to_ocrmypdf_sidecar(tmp_path: Path, monkeypatch) -> None:
    pdf = tmp_path / "image-only.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        if args[0] == "pdftotext":
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="\f\n")
        if args[0] == "ocrmypdf":
            Path(args[2]).write_text("OCR text from scanned pages", encoding="utf-8")
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="")
        raise AssertionError(args)

    monkeypatch.setattr(subprocess, "run", fake_run)

    doc = adapt_document(pdf, display_root=tmp_path)

    assert doc.metadata["extraction"] == "ocrmypdf-sidecar"
    assert doc.text == "OCR text from scanned pages"
    assert calls[0][0][0] == "pdftotext"
    assert calls[1][0][0] == "ocrmypdf"
