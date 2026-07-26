from pathlib import Path
import pytest

from didactopus.config import load_config
from didactopus.config import PlatformConfig
from didactopus.roles import role_ids


def test_load_example_config() -> None:
    config = load_config(Path("configs/config.example.yaml"))
    assert config.platform.dimension_thresholds["transfer"] == 0.7
    assert config.platform.evidence_coverage_threshold == 0.8
    assert config.model_provider.provider == "stub"


def test_legacy_platform_confidence_threshold_warns() -> None:
    with pytest.warns(DeprecationWarning, match="evidence_coverage_threshold"):
        config = PlatformConfig(confidence_threshold=0.7)

    assert config.evidence_coverage_threshold == 0.7


def test_load_rolemesh_config() -> None:
    config = load_config(Path("configs/config.rolemesh.example.yaml"))
    assert config.model_provider.provider == "rolemesh"
    assert config.model_provider.rolemesh.role_to_model["mentor"] == "planner"
    assert config.model_provider.rolemesh.role_to_model["learner"] == "writer"
    assert set(config.model_provider.rolemesh.role_to_model) == set(role_ids())


def test_load_geniehive_config() -> None:
    config = load_config(Path("configs/config.geniehive.example.yaml"))
    assert config.model_provider.provider == "geniehive"
    assert config.model_provider.geniehive.role_to_model["mentor"] == "planner"
    assert config.model_provider.geniehive.role_to_model["learner"] == "writer"
    assert set(config.model_provider.geniehive.role_to_model) == set(role_ids())
    assert config.model_provider.gateway.base_url == config.model_provider.geniehive.base_url
