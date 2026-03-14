from __future__ import annotations
import json
from pathlib import Path

def color_for_status(status: str) -> str:
    return {
        "mastered": "#1f7a1f",
        "active": "#2d6cdf",
        "available": "#c48a00",
        "locked": "#9aa4b2",
    }.get(status, "#9aa4b2")

def frame_to_svg(frame: dict, width: int = 960, height: int = 560) -> str:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#fbfcfe"/>')
    for edge in frame.get("edges", []):
        src = next((n for n in frame["nodes"] if n["id"] == edge["source"]), None)
        dst = next((n for n in frame["nodes"] if n["id"] == edge["target"]), None)
        if src and dst:
            parts.append(f'<line x1="{src["x"]}" y1="{src["y"]}" x2="{dst["x"]}" y2="{dst["y"]}" stroke="#b8c2cf" stroke-width="3"/>')
    for node in frame.get("nodes", []):
        fill = color_for_status(node["status"])
        parts.append(f'<circle cx="{node["x"]}" cy="{node["y"]}" r="{node["size"]}" fill="{fill}" />')
        parts.append(f'<text x="{node["x"]}" y="{node["y"]-4}" font-size="12" text-anchor="middle" fill="white">{node["title"]}</text>')
        parts.append(f'<text x="{node["x"]}" y="{node["y"]+14}" font-size="10" text-anchor="middle" fill="white">{node["score"]:.2f} · {node["status"]}</text>')
    parts.append("</svg>")
    return "".join(parts)

def export_svg_frames(payload_path: str, out_dir: str):
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for frame in payload.get("frames", []):
        svg = frame_to_svg(frame)
        (out / f'frame_{frame["index"]:04d}.svg').write_text(svg, encoding="utf-8")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("payload_json")
    parser.add_argument("out_dir")
    args = parser.parse_args()
    export_svg_frames(args.payload_json, args.out_dir)
    print(f"Exported SVG frames to {args.out_dir}")
