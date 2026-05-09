from __future__ import annotations

from pathlib import Path
import json
import yaml


def load_augmentation_bundle(bundle_dir: str | Path) -> dict[str, str]:
    base = Path(bundle_dir)
    manifest_path = None
    for candidate in ("bundle.yaml", "bundle.yml", "bundle.json"):
        path = base / candidate
        if path.exists():
            manifest_path = path
            break

    payload: dict = {}
    if manifest_path is not None:
        raw = manifest_path.read_text(encoding="utf-8")
        if manifest_path.suffix.lower() == ".json":
            payload = json.loads(raw) if raw.strip() else {}
        else:
            payload = yaml.safe_load(raw) or {}

    snippets_dir = payload.get("snippets_dir", "snippets")
    source_inventory = payload.get("source_inventory", "wolfe-sources.yaml")
    concept_alignment = payload.get("concept_alignment", "snippets/concept-alignment.yaml")

    resolved_snippets = (base / snippets_dir).resolve()
    resolved_inventory = (base / source_inventory).resolve()
    resolved_alignment = (base / concept_alignment).resolve()

    return {
        "bundle_dir": str(base.resolve()),
        "snippets_dir": str(resolved_snippets),
        "source_inventory": str(resolved_inventory),
        "concept_alignment": str(resolved_alignment),
        "title": str(payload.get("title", base.name)),
        "description": str(payload.get("description", "")),
    }
