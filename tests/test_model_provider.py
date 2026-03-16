from didactopus.config import ModelProviderConfig
from didactopus.model_provider import ModelProvider
from didactopus.role_prompts import evaluator_system_prompt, mentor_system_prompt


def test_stub_provider_includes_role_marker() -> None:
    provider = ModelProvider(ModelProviderConfig())
    response = provider.generate("Explain entropy simply.", role="mentor")
    assert response.provider == "stub"
    assert "[mentor]" in response.text


def test_rolemesh_provider_uses_role_mapping() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "rolemesh",
            "rolemesh": {
                "base_url": "http://127.0.0.1:8000",
                "api_key": "demo",
                "default_model": "planner",
                "role_to_model": {"mentor": "planner", "practice": "writer"},
            },
        }
    )
    provider = ModelProvider(config)

    def fake_chat(payload: dict) -> dict:
        assert payload["model"] == "writer"
        assert payload["messages"][0]["role"] == "system"
        return {"choices": [{"message": {"content": "Practice task response"}}]}

    provider._rolemesh_chat_completion = fake_chat  # type: ignore[method-assign]
    response = provider.generate(
        "Generate a practice task.",
        role="practice",
        system_prompt="System prompt",
    )
    assert response.provider == "rolemesh"
    assert response.model_name == "writer"
    assert response.text == "Practice task response"


def test_rolemesh_provider_emits_pending_notice() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "rolemesh",
            "rolemesh": {
                "base_url": "http://127.0.0.1:8000",
                "api_key": "demo",
                "default_model": "planner",
                "role_to_model": {"evaluator": "reviewer"},
            },
        }
    )
    provider = ModelProvider(config)
    seen: list[str] = []

    def fake_chat(payload: dict) -> dict:
        return {"choices": [{"message": {"content": "Evaluation response"}}]}

    provider._rolemesh_chat_completion = fake_chat  # type: ignore[method-assign]
    response = provider.generate(
        "Evaluate a learner answer.",
        role="evaluator",
        status_callback=seen.append,
    )

    assert response.text == "Evaluation response"
    assert seen == ["Didactopus is evaluating the work before replying. Model: reviewer."]


def test_evaluator_prompt_requires_checking_existing_caveats() -> None:
    prompt = evaluator_system_prompt().lower()
    assert "before saying something is missing" in prompt
    assert "quote or paraphrase" in prompt
    assert "do not invent omissions" in prompt


def test_mentor_prompt_requires_acknowledging_existing_caveats() -> None:
    prompt = mentor_system_prompt().lower()
    assert "acknowledge what the learner already did correctly" in prompt
    assert "do not claim a caveat" in prompt
