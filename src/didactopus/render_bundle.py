from __future__ import annotations
import json
from pathlib import Path
from .export_svg import export_svg_frames

def make_render_bundle(payload_json: str, out_dir: str, fps: int = 2, fmt: str = "gif"):
    out = Path(out_dir)
    frames_dir = out / "frames"
    out.mkdir(parents=True, exist_ok=True)
    export_svg_frames(payload_json, str(frames_dir))
    manifest = {
        "input_payload": payload_json,
        "frames_dir": str(frames_dir),
        "fps": fps,
        "format": fmt,
        "expected_output": str(out / f"animation.{fmt}"),
        "ffmpeg_example": f"ffmpeg -framerate {fps} -pattern_type glob -i '{frames_dir}/*.svg' {out / ('animation.' + fmt)}",
    }
    (out / "render_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    script = "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"ffmpeg -framerate {fps} -pattern_type glob -i '{frames_dir}/*.svg' '{out / ('animation.' + fmt)}'",
    ])
    (out / "render.sh").write_text(script, encoding="utf-8")
