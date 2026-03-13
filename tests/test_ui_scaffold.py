from pathlib import Path
from didactopus.ui_scaffold import write_review_ui


def test_write_ui(tmp_path: Path) -> None:
    write_review_ui(tmp_path)
    assert (tmp_path / "index.html").exists()
