from pathlib import Path

def test_frontend_scaffold_exists():
    assert Path("webui/src/App.jsx").exists()
    assert Path("webui/src/api.js").exists()
