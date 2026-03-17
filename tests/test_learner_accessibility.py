from pathlib import Path

from didactopus.learner_accessibility import (
    build_accessible_session_html,
    build_accessible_session_text,
    render_accessible_session_outputs,
)
from didactopus.learner_session_demo import run_learner_session_demo


def _session_payload() -> dict:
    root = Path(__file__).resolve().parents[1]
    return run_learner_session_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
    )


def test_accessible_session_html_has_landmarks() -> None:
    html = build_accessible_session_html(_session_payload())
    assert 'href="#session-main"' in html
    assert 'aria-label="Didactopus learner session"' in html
    assert "Study Plan" in html
    assert "Conversation" in html
    assert "Evaluation Summary" in html


def test_accessible_session_text_is_linearized() -> None:
    text = build_accessible_session_text(_session_payload())
    assert "Learner goal:" in text
    assert "Source language:" in text
    assert "Output language:" in text
    assert "Study plan:" in text
    assert "Conversation:" in text
    assert "Evaluation summary:" in text


def test_render_accessible_session_outputs_writes_files(tmp_path: Path) -> None:
    outputs = render_accessible_session_outputs(
        _session_payload(),
        out_html=tmp_path / "session.html",
        out_text=tmp_path / "session.txt",
    )
    assert Path(outputs["html"]).exists()
    assert Path(outputs["text"]).exists()
