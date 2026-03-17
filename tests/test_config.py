from pathlib import Path
from didactopus.config import load_config
from didactopus.roles import role_ids


def test_load_example_config() -> None:
    config = load_config(Path("configs/config.example.yaml"))
    assert config.platform.dimension_thresholds["transfer"] == 0.7
    assert config.platform.confidence_threshold == 0.8
    assert config.model_provider.provider == "stub"


def test_load_rolemesh_config() -> None:
    config = load_config(Path("configs/config.rolemesh.example.yaml"))
    assert config.model_provider.provider == "rolemesh"
    assert config.model_provider.rolemesh.role_to_model["mentor"] == "planner"
    assert config.model_provider.rolemesh.role_to_model["learner"] == "writer"
    assert set(config.model_provider.rolemesh.role_to_model) == set(role_ids())


def test_load_ollama_config() -> None:
    config = load_config(Path("configs/config.ollama.example.yaml"))
    assert config.model_provider.provider == "ollama"
    assert config.model_provider.ollama.base_url.endswith("/v1")
    assert set(config.model_provider.ollama.role_to_model) == set(role_ids())


def test_load_openai_compatible_config() -> None:
    config = load_config(Path("configs/config.openai-compatible.example.yaml"))
    assert config.model_provider.provider == "openai_compatible"
    assert config.model_provider.openai_compatible.base_url == "https://api.openai.com/v1"
    assert set(config.model_provider.openai_compatible.role_to_model) == set(role_ids())
