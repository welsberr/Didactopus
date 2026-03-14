from pathlib import Path

def test_python_scaffold_exists():
    assert Path("src/didactopus/learner_state.py").exists()
    assert Path("src/didactopus/progression_engine.py").exists()
