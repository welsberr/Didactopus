from pathlib import Path

from didactopus.config import ModelProviderConfig
from didactopus.model_provider import ModelProvider
from didactopus.ocw_rolemesh_transcript_demo import (
    _apply_gateway_fallbacks,
    _healthy_gateway_models,
    _healthy_rolemesh_models,
    _looks_truncated,
    run_ocw_rolemesh_transcript_demo,
)


def test_looks_truncated_detects_prose_cutoff_before_numbered_list() -> None:
    text = (
        "Suppose we have a binary symmetric channel with crossover\n\n"
        "1. Estimate the error probability.\n"
        "2. Relate it to capacity."
    )
    assert _looks_truncated(text) is True


def test_looks_truncated_detects_common_cutoff_phrase() -> None:
    assert _looks_truncated("Furthermore") is True
    assert _looks_truncated("Compare the entropy of one roll with the") is True


def test_ocw_rolemesh_transcript_demo_writes_artifacts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = run_ocw_rolemesh_transcript_demo(
        root / "configs" / "config.example.yaml",
        root / "skills" / "ocw-information-entropy-agent",
        tmp_path,
    )

    assert payload["provider"] == "stub"
    assert len(payload["transcript"]) >= 16
    assert len(payload["curriculum_path_titles"]) >= 8
    assert payload["graph_grounding_summary"]["node_count"] >= 1
    assert payload["model_fallbacks"] == {}
    assert payload["role_fallbacks"] == {}
    assert payload["provider_diagnostics"]["provider"] == "stub"
    assert payload["provider_diagnostics"]["role_model_overrides"] == {}
    assert payload["status_updates"] == []
    assert any(turn["speaker"] == "Didactopus Evaluator" for turn in payload["transcript"])
    assert any("channel" in turn["content"].lower() for turn in payload["transcript"])
    assert any("thermodynamic" in turn["content"].lower() for turn in payload["transcript"])
    assert any("supporting lessons" in turn["content"].lower() or "grounding fragments" in turn["content"].lower() for turn in payload["transcript"])
    assert all(not _looks_truncated(turn["content"]) for turn in payload["transcript"])
    assert (tmp_path / "rolemesh_transcript.json").exists()
    assert (tmp_path / "rolemesh_transcript.md").exists()
    assert "Pending Status Examples" not in (tmp_path / "rolemesh_transcript.md").read_text(encoding="utf-8")


def test_gateway_fallbacks_use_generic_model_catalog() -> None:
    config = ModelProviderConfig.model_validate(
        {
            "provider": "geniehive",
            "geniehive": {
                "default_model": "planner",
                "role_to_model": {"mentor": "planner", "practice": "writer", "evaluator": "reviewer"},
            },
        }
    )
    provider = ModelProvider(config)
    provider.list_models = lambda: [  # type: ignore[method-assign]
        {
            "id": "planner",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 1, "loaded_target_count": 1, "best_p50_latency_ms": 1200},
        },
        {
            "id": "reviewer",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 1, "loaded_target_count": 0, "best_p50_latency_ms": 1800},
        },
        {
            "id": "writer",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 0, "loaded_target_count": 0, "best_p50_latency_ms": 800},
        },
    ]
    provider.resolve_route = lambda model, *, kind=None: {  # type: ignore[method-assign]
        "match_type": "role",
        "service": {"service_id": f"svc::{model}"},
    } if model in {"planner", "reviewer"} and kind == "chat" else None

    assert _healthy_rolemesh_models(provider) == {"planner", "reviewer"}
    assert _healthy_gateway_models(provider) == {"planner", "reviewer"}
    assert _apply_gateway_fallbacks(provider) == {"practice": "planner"}
    assert config.geniehive.role_to_model["practice"] == "writer"


def test_gateway_fallbacks_prefer_routable_loaded_role_aliases() -> None:
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
            "id": "slow-asset",
            "geniehive": {"route_type": "asset", "operation": "chat", "health": "healthy", "loaded_asset_count": 1, "best_p50_latency_ms": 5000},
        },
        {
            "id": "mentor-role",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 1, "loaded_target_count": 1, "best_p50_latency_ms": 900},
        },
        {
            "id": "practice-role",
            "geniehive": {"route_type": "role", "operation": "chat", "healthy_target_count": 0, "loaded_target_count": 0, "best_p50_latency_ms": 200},
        },
    ]
    provider.resolve_route = lambda model, *, kind=None: {  # type: ignore[method-assign]
        "match_type": "role",
        "service": {"service_id": f"svc::{model}"},
    } if model == "mentor-role" and kind == "chat" else None

    assert _apply_gateway_fallbacks(provider) == {"practice": "mentor-role"}
    assert config.geniehive.role_to_model["practice"] == "practice-role"
