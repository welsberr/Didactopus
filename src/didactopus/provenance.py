from __future__ import annotations
from pathlib import Path
import json, yaml
from .source_models import SourceInventory

def load_sources(path: str | Path) -> SourceInventory:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return SourceInventory.model_validate(data)

def build_provenance_manifest(inventory: SourceInventory) -> dict:
    return {
        "source_count": len(inventory.sources),
        "sources": [s.model_dump() for s in inventory.sources],
        "licenses_present": sorted({s.license_id for s in inventory.sources if s.license_id}),
        "excluded_source_count": sum(1 for s in inventory.sources if s.excluded_from_upstream_license),
        "adapted_source_count": sum(1 for s in inventory.sources if s.adapted),
    }

def write_provenance_manifest(inventory: SourceInventory, outpath: str | Path) -> None:
    Path(outpath).write_text(json.dumps(build_provenance_manifest(inventory), indent=2), encoding="utf-8")
