from pathlib import Path

def test_scaffold_files_exist():
    assert Path("src/didactopus/api.py").exists()
    assert Path("src/didactopus/repository.py").exists()
    assert Path("src/didactopus/worker.py").exists()
    assert Path("src/didactopus/knowledge_export.py").exists()
    assert Path("FAQ.md").exists()
