from pathlib import Path

from didactopus.ocw_progress_viz import render_ocw_full_concept_map, render_ocw_progress_visualization


def test_render_ocw_progress_visualization(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    outputs = render_ocw_progress_visualization(
        root / "examples" / "ocw-information-entropy-run",
        tmp_path / "progress.svg",
        tmp_path / "progress.html",
    )

    assert Path(outputs["svg"]).exists()
    assert Path(outputs["html"]).exists()
    assert "learner_progress" not in Path(outputs["svg"]).read_text(encoding="utf-8")
    assert "MASTERED" in Path(outputs["svg"]).read_text(encoding="utf-8")


def test_render_ocw_full_concept_map(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    outputs = render_ocw_full_concept_map(
        root / "examples" / "ocw-information-entropy-run",
        root / "domain-packs" / "mit-ocw-information-entropy",
        tmp_path / "full.svg",
        tmp_path / "full.html",
    )

    svg = Path(outputs["svg"]).read_text(encoding="utf-8")
    assert Path(outputs["svg"]).exists()
    assert Path(outputs["html"]).exists()
    assert "Full Concept Map" in svg
    assert "extractor spillover" in svg
