from __future__ import annotations

import json
from pathlib import Path

from .gateway_demo import run_gateway_demo


def run_rolemesh_demo(config_path: str | Path, out_path: str | Path | None = None) -> dict:
    return run_gateway_demo(config_path, out_path)


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Compatibility wrapper for the older RoleMesh-named Didactopus demo.")
    parser.add_argument(
        "--config",
        default=str(root / "configs" / "config.rolemesh.example.yaml"),
    )
    parser.add_argument(
        "--out",
        default=str(root / "examples" / "rolemesh_demo.json"),
    )
    args = parser.parse_args()
    payload = run_rolemesh_demo(args.config, args.out)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
