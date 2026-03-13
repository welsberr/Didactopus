from pathlib import Path
from didactopus.config import load_config


def test_load_example_config() -> None:
    config = load_config(Path("configs/config.example.yaml"))
    assert config.platform.dimension_thresholds["transfer"] == 0.7
    assert config.platform.confidence_threshold == 0.8
