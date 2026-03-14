from pathlib import Path

def test_backend_scaffold_exists():
    assert Path("src/didactopus/api.py").exists()
    assert Path("src/didactopus/orm.py").exists()
    assert Path("src/didactopus/seed.py").exists()
