from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_scaffold_exists():
    assert (ROOT / "webui/src/App.jsx").exists()
    assert (ROOT / "webui/src/api.js").exists()
