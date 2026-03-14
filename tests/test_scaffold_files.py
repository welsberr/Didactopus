from pathlib import Path

def test_scaffold_files_exist():
    assert Path("src/didactopus/api.py").exists()
    assert Path("src/didactopus/repository.py").exists()
    assert Path("src/didactopus/orm.py").exists()
    assert Path("webui/src/App.jsx").exists()
