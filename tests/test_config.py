from pathlib import Path
from didactopus.config import load_config


def test_load_example_config() -> None:
    config = load_config(Path("configs/config.example.yaml"))
    assert config.model_provider.mode == "local_first"
    assert config.platform.verification_required is True
    assert config.platform.mastery_threshold == 0.8
    assert "domain-packs" in config.artifacts.local_pack_dirs
