from __future__ import annotations
from pathlib import Path
import argparse, json, yaml

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def convert_pack(pack_dir: str | Path) -> dict:
    pack_dir = Path(pack_dir)
    pack = load_yaml(pack_dir / "pack.yaml")
    concepts_data = load_yaml(pack_dir / "concepts.yaml")
    compliance_path = pack_dir / "pack_compliance_manifest.json"
    compliance = json.loads(compliance_path.read_text(encoding="utf-8")) if compliance_path.exists() else {}

    concepts = []
    for item in concepts_data.get("concepts", []) or []:
        concepts.append({
            "id": item.get("id"),
            "title": item.get("title", item.get("id", "")),
            "prerequisites": list(item.get("prerequisites", []) or []),
            "masteryDimension": "mastery",
            "exerciseReward": f"{item.get('title', item.get('id', 'Concept'))} progress recorded",
        })

    onboarding = {
        "headline": pack.get("first_session_headline", f"Start with {concepts[0]['title']}" if concepts else "Start here"),
        "body": pack.get("first_session_body", "Begin with one short activity and get a visible mastery marker."),
        "checklist": list(pack.get("first_session_checklist", [
            "Read the short orientation",
            "Try one guided exercise",
            "Write one explanation in your own words",
        ])),
    }

    return {
        "id": pack.get("name", pack_dir.name),
        "title": pack.get("display_name", pack.get("name", pack_dir.name)),
        "subtitle": pack.get("description", ""),
        "level": pack.get("audience_level", "novice-friendly"),
        "concepts": concepts,
        "onboarding": onboarding,
        "compliance": {
            "sources": len(compliance.get("derived_from_sources", []) or []),
            "attributionRequired": bool(compliance.get("attribution_required", False)),
            "shareAlikeRequired": bool(compliance.get("share_alike_required", False)),
            "noncommercialOnly": bool(compliance.get("noncommercial_only", False)),
            "flags": list(compliance.get("restrictive_flags", []) or []),
        },
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Didactopus pack directory to learner-frontend JSON.")
    parser.add_argument("pack_dir")
    parser.add_argument("--out", default="pack.frontend.json")
    args = parser.parse_args()
    payload = convert_pack(args.pack_dir)
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
