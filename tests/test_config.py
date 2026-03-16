from pathlib import Path
from didactopus.config import load_config


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
