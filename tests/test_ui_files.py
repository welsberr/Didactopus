from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ui_files_exist():
    assert (ROOT / "webui/src/App.jsx").exists()
    assert (ROOT / "webui/src/storage.js").exists()
    assert (ROOT / "webui/public/packs/bayes-pack.json").exists()
    assert (ROOT / "webui/public/packs/evidence-trail-pack.json").exists()
