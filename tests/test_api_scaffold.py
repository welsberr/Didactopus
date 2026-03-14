from pathlib import Path

def test_api_files_exist():
    assert Path("src/didactopus/api.py").exists()
    assert Path("src/didactopus/storage.py").exists()
    assert Path("data/packs/bayes-pack.json").exists()
