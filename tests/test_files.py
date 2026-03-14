from pathlib import Path

def test_scaffold_files_exist():
    assert Path("src/didactopus/api.py").exists()
    assert Path("src/didactopus/worker.py").exists()
    assert Path("docker-compose.yml").exists()
    assert Path("webui/src/App.jsx").exists()
