from didactopus.pedagogy import communication_boundaries


def test_communication_notice_states_humane_boundaries():
    notice = communication_boundaries()
    assert "Participation:" in notice and "Privacy:" in notice
    assert "not counseling" in notice
    assert "Escalation:" in notice
