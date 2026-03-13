from pathlib import Path


def test_webui_scaffold_exists() -> None:
    assert Path("webui/src/App.jsx").exists()
    assert Path("webui/sample/review_data.json").exists()
