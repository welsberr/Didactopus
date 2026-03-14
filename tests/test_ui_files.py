from pathlib import Path

def test_ui_files_exist():
    assert Path("webui/src/App.jsx").exists()
    assert Path("webui/src/storage.js").exists()
    assert Path("webui/public/packs/bayes-pack.json").exists()
