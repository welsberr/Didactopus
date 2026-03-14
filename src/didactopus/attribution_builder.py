from __future__ import annotations
from pathlib import Path
import argparse
from .provenance import load_sources, write_provenance_manifest

def render_attribution_markdown(sources_path: str | Path) -> str:
    inventory = load_sources(sources_path)
    lines = ["# Attribution", ""]
    for src in inventory.sources:
        lines.append(f"## {src.title}")
        lines.append(f"- Source ID: {src.source_id}")
        lines.append(f"- URL: {src.url}")
        if src.creator:
            lines.append(f"- Creator: {src.creator}")
        if src.publisher:
            lines.append(f"- Publisher: {src.publisher}")
        if src.license_id:
            lines.append(f"- License: {src.license_id}")
        if src.license_url:
            lines.append(f"- License URL: {src.license_url}")
        lines.append(f"- Adapted: {'yes' if src.adapted else 'no'}")
        if src.adaptation_notes:
            lines.append(f"- Adaptation notes: {src.adaptation_notes}")
        if src.attribution_text:
            lines.append(f"- Attribution text: {src.attribution_text}")
        if src.excluded_from_upstream_license:
            lines.append(f"- Excluded from upstream course license: yes")
        if src.exclusion_notes:
            lines.append(f"- Exclusion notes: {src.exclusion_notes}")
        lines.append("")
    return "\n".join(lines)

def build_artifacts(sources_path: str | Path, attribution_out: str | Path, manifest_out: str | Path) -> None:
    Path(attribution_out).write_text(render_attribution_markdown(sources_path), encoding="utf-8")
    inventory = load_sources(sources_path)
    write_provenance_manifest(inventory, manifest_out)

def main() -> None:
    parser = argparse.ArgumentParser(description="Build Didactopus attribution artifacts from sources.yaml")
    parser.add_argument("sources")
    parser.add_argument("--attribution-out", default="ATTRIBUTION.md")
    parser.add_argument("--manifest-out", default="provenance_manifest.json")
    args = parser.parse_args()
    build_artifacts(args.sources, args.attribution_out, args.manifest_out)

if __name__ == "__main__":
    main()
