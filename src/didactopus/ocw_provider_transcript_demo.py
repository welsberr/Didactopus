from __future__ import annotations

import json
from pathlib import Path

from .ocw_rolemesh_transcript_demo import (
    build_ocw_rolemesh_transcript,
    write_transcript_artifacts as _write_legacy_transcript_artifacts,
)


def build_ocw_provider_transcript(config_path: str | Path, skill_dir: str | Path) -> dict:
    return build_ocw_rolemesh_transcript(config_path, skill_dir)


def write_transcript_artifacts(
    payload: dict,
    out_dir: str | Path,
    *,
    stem: str = "provider_transcript",
) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    legacy = _write_legacy_transcript_artifacts(payload, out_dir)
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    Path(legacy["json"]).replace(json_path)
    Path(legacy["md"]).replace(md_path)
    return {"json": str(json_path), "md": str(md_path)}


def run_ocw_provider_transcript_demo(config_path: str | Path, skill_dir: str | Path, out_dir: str | Path) -> dict:
    payload = build_ocw_provider_transcript(config_path, skill_dir)
    outputs = write_transcript_artifacts(payload, out_dir)
    payload["artifacts"] = outputs
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a transcript of an AI learner using a gateway-backed provider to approach the MIT OCW Information and Entropy course.")
    parser.add_argument("--config", default=str(root / "configs" / "config.geniehive.example.yaml"))
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out-dir", default=str(root / "examples" / "ocw-information-entropy-provider-transcript"))
    args = parser.parse_args()
    payload = run_ocw_provider_transcript_demo(args.config, args.skill_dir, args.out_dir)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
