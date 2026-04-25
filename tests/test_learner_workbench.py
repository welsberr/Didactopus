from didactopus import learner_workbench as learner_workbench_module


class _FakeProvider:
    def __init__(self, _config) -> None:
        pass

    def generate(
        self,
        prompt: str,
        *,
        role: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        return type(
            "Response",
            (),
            {
                "text": f"{role}: {prompt.splitlines()[0]}",
                "provider": "fake",
                "model_name": "fake-model",
            },
        )()


def test_build_pack_workbench_session_uses_evidence_trail_pack(monkeypatch) -> None:
    monkeypatch.setattr(learner_workbench_module, "ModelProvider", _FakeProvider)

    payload = learner_workbench_module.build_pack_workbench_session(
        pack_id="evidence-trail",
        concept_id="question-framing",
        learner_goal="Understand how to compare evidence.",
        question="Which question should guide the study step?",
        observation="The pack starts with question framing.",
        interpretation="Question framing organizes the next evidence move.",
        uncertainty="I do not yet know which source will best test the interpretation.",
        revision_trigger="A stronger source trail could change the current framing.",
    )

    assert payload["pack_id"] == "evidence-trail"
    assert payload["concept_id"] == "question-framing"
    assert payload["next_concept_id"] == "observation-vs-interpretation"
    assert payload["mentor"]["provider"] == "fake"
    assert payload["feedback"]["strengths"]
    assert payload["feedback"]["gaps"] == []
