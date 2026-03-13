from pathlib import Path
from didactopus.config import load_config


def test_load_example_config() -> None:
    config = load_config(Path("configs/config.example.yaml"))
    assert config.platform.evidence_weights["project"] == 2.5
    assert config.platform.recent_evidence_multiplier == 1.35
