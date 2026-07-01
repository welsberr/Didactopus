from didactopus.config import ModelProviderConfig
from didactopus.model_provider import ModelProvider
from didactopus.provider_policy import effective_provider_for_kind, provider_diagnostics_for_kind
from didactopus.role_prompts import evaluator_system_prompt, mentor_system_prompt, system_prompt_for_role


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


def test_geniehive_provider_uses_role_mapping() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "base_url": "http://127.0.0.1:8800",
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

    provider._gateway_chat_completion = fake_chat  # type: ignore[method-assign]
    response = provider.generate(
        "Generate a practice task.",
        role="practice",
        system_prompt="System prompt",
    )
    assert response.provider == "geniehive"
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


def test_geniehive_provider_lists_models() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "base_url": "http://127.0.0.1:8800",
                "api_key": "demo",
                "default_model": "planner",
                "role_to_model": {"mentor": "planner"},
            },
        }
    )
    provider = ModelProvider(config)

    def fake_list() -> list[dict]:
        return [{"id": "planner", "status": "ready"}, {"id": "writer", "healthy": True}]

    provider._gateway_list_models = fake_list  # type: ignore[method-assign]
    assert provider.list_models() == [{"id": "planner", "status": "ready"}, {"id": "writer", "healthy": True}]


def test_geniehive_provider_resolves_route() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "base_url": "http://127.0.0.1:8800",
                "api_key": "demo",
                "default_model": "planner",
                "role_to_model": {"mentor": "planner"},
            },
        }
    )
    provider = ModelProvider(config)

    def fake_resolve(model: str, *, kind: str | None = None) -> dict | None:
        assert model == "planner"
        assert kind == "chat"
        return {"match_type": "role", "service": {"service_id": "atlas-01/chat/qwen3-8b"}}

    provider._gateway_resolve_route = fake_resolve  # type: ignore[method-assign]
    assert provider.resolve_route("planner", kind="chat") == {
        "match_type": "role",
        "service": {"service_id": "atlas-01/chat/qwen3-8b"},
    }


def test_with_role_model_overrides_prefers_override_mapping() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "default_model": "planner",
                "role_to_model": {"mentor": "planner", "practice": "writer"},
            },
        }
    )
    provider = ModelProvider(config).with_role_model_overrides({"practice": "fallback-writer"})

    def fake_chat(payload: dict) -> dict:
        assert payload["model"] == "fallback-writer"
        return {"choices": [{"message": {"content": "Practice task response"}}]}

    provider._gateway_chat_completion = fake_chat  # type: ignore[method-assign]
    response = provider.generate("Generate a practice task.", role="practice")
    assert response.model_name == "fallback-writer"
    assert response.text == "Practice task response"


def test_effective_provider_for_kind_applies_resolved_overrides() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "default_model": "planner",
                "role_to_model": {"mentor": "mentor-role", "practice": "practice-role"},
            },
        }
    )
    provider = ModelProvider(config)
    provider.list_models = lambda: [  # type: ignore[method-assign]
        {
            "id": "mentor-role",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 1, "loaded_target_count": 1},
        }
    ]
    provider.resolve_route = lambda model, *, kind=None: {  # type: ignore[method-assign]
        "match_type": "role",
        "service": {"service_id": f"svc::{model}"},
    } if model == "mentor-role" and kind == "chat" else None

    effective = effective_provider_for_kind(provider, kind="chat")
    assert effective is not provider
    assert effective.role_model_overrides == {"practice": "mentor-role"}
    assert config.geniehive.role_to_model["practice"] == "practice-role"


def test_provider_diagnostics_for_kind_reports_routes_and_overrides() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "default_model": "planner",
                "role_to_model": {"mentor": "mentor-role", "practice": "practice-role"},
            },
        }
    )
    provider = ModelProvider(config)
    provider.list_models = lambda: [  # type: ignore[method-assign]
        {
            "id": "mentor-role",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 1, "loaded_target_count": 1},
        }
    ]
    provider.resolve_route = lambda model, *, kind=None: {  # type: ignore[method-assign]
        "match_type": "role",
        "service": {"service_id": f"svc::{model}"},
    } if model == "mentor-role" and kind == "chat" else None

    diagnostics = provider_diagnostics_for_kind(provider, kind="chat")
    assert diagnostics["provider"] == "geniehive"
    assert diagnostics["healthy_models"] == ["mentor-role"]
    assert diagnostics["fallback_model"] == "mentor-role"
    assert diagnostics["role_model_overrides"] == {"practice": "mentor-role"}
    assert diagnostics["routes"]["mentor"]["requested_model"] == "mentor-role"
    assert diagnostics["routes"]["practice"]["requested_model"] == "mentor-role"
    assert diagnostics["routes"]["mentor"]["resolution"]["service"]["service_id"] == "svc::mentor-role"


def test_evaluator_prompt_requires_checking_existing_caveats() -> None:
    prompt = evaluator_system_prompt().lower()
    assert "before saying something is missing" in prompt
    assert "quote or paraphrase" in prompt
    assert "do not invent omissions" in prompt


def test_mentor_prompt_requires_acknowledging_existing_caveats() -> None:
    prompt = mentor_system_prompt().lower()
    assert "acknowledge what the learner already did correctly" in prompt
    assert "do not claim a caveat" in prompt


def test_system_prompt_for_role_covers_defined_roles() -> None:
    assert "mentor mode" in system_prompt_for_role("mentor").lower()
    assert "practice-design mode" in system_prompt_for_role("practice").lower()
