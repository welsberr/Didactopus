from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .model_provider import ModelProvider
from .provider_policy import provider_diagnostics_for_kind


def inspect_provider(config_path: str | Path, *, kind: str = "chat", out_path: str | Path | None = None) -> dict:
    config = load_config(config_path)
    payload = provider_diagnostics_for_kind(ModelProvider(config.model_provider), kind=kind)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def build_parser() -> argparse.ArgumentParser:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Inspect Didactopus provider routing, overrides, and resolved routes.")
    parser.add_argument("--config", default=str(root / "configs" / "config.geniehive.example.yaml"))
    parser.add_argument("--kind", default="chat")
    parser.add_argument("--out")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    payload = inspect_provider(args.config, kind=args.kind, out_path=args.out)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
