from pathlib import Path

from didactopus.notebook_learning_sequence_demo import run_notebook_learning_sequence_demo
from didactopus.notebook_learning_sequence import DEFAULT_SEQUENCE_PATH


def test_run_notebook_learning_sequence_demo_writes_output(tmp_path: Path) -> None:
    out_path = tmp_path / "sequence-plan.json"

    payload = run_notebook_learning_sequence_demo(DEFAULT_SEQUENCE_PATH, out_path)

    assert out_path.exists()
    assert payload["session_count"] == 3
    assert payload["sessions"][0]["title"] == "Observation"
    assert payload["sessions"][-1]["title"] == "Qualified Conclusion"
