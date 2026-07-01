from pathlib import Path

from didactopus.notebook_learning_sequence_demo import run_notebook_learning_sequence_demo


def test_run_notebook_learning_sequence_demo_writes_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    sequence = (
        root
        / "evo-edu.org"
        / "notebook"
        / "learning-paths"
        / "foundations-first-ring.didactopus.json"
    )
    out_path = tmp_path / "sequence-plan.json"

    payload = run_notebook_learning_sequence_demo(sequence, out_path)

    assert out_path.exists()
    assert payload["session_count"] == 8
    assert payload["sessions"][0]["title"] == "Allele Frequency Change"
    assert payload["sessions"][-1]["title"] == "Common Descent"
