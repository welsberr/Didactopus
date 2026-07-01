from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_api_files_exist():
    assert (ROOT / "src/didactopus/api.py").exists()
    assert (ROOT / "src/didactopus/storage.py").exists()
    assert (ROOT / "src/didactopus/learner_workbench.py").exists()
    assert (ROOT / "data/packs/bayes-pack.json").exists()
