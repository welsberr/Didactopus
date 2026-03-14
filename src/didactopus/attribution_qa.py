from __future__ import annotations
from pathlib import Path
from .provenance import load_sources

def attribution_qa(sources_path: str | Path) -> dict:
    inv = load_sources(sources_path)
    warnings: list[str] = []

    for src in inv.sources:
        if not src.license_id:
            warnings.append(f"Source '{src.source_id}' is missing a license identifier.")
        if src.license_id and not src.license_url:
            warnings.append(f"Source '{src.source_id}' is missing a license URL.")
        if not src.attribution_text:
            warnings.append(f"Source '{src.source_id}' is missing attribution text.")
        if not src.url:
            warnings.append(f"Source '{src.source_id}' is missing a source URL.")
        if src.adapted and not src.adaptation_notes:
            warnings.append(f"Source '{src.source_id}' is marked adapted but has no adaptation notes.")
        if src.excluded_from_upstream_license and not src.exclusion_notes:
            warnings.append(f"Source '{src.source_id}' is marked excluded but has no exclusion notes.")

    summary = {
        "warning_count": len(warnings),
        "source_count": len(inv.sources),
        "adapted_source_count": sum(1 for s in inv.sources if s.adapted),
        "excluded_source_count": sum(1 for s in inv.sources if s.excluded_from_upstream_license),
    }
    return {"warnings": warnings, "summary": summary}
