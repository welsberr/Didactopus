from __future__ import annotations
from pathlib import Path
import argparse, json, yaml
from .compliance_models import SourceInventory, PackComplianceManifest

def load_sources(path: str | Path) -> SourceInventory:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return SourceInventory.model_validate(data)

def build_pack_compliance_manifest(
    pack_id: str,
    display_name: str,
    inventory: SourceInventory,
) -> PackComplianceManifest:
    licenses = {s.license_id for s in inventory.sources if s.license_id}
    restrictive_flags: list[str] = []
    redistribution_notes: list[str] = []

    share_alike_required = any("SA" in lic for lic in licenses)
    noncommercial_only = any("NC" in lic for lic in licenses)

    if share_alike_required:
        restrictive_flags.append("share-alike")
        redistribution_notes.append("Derived redistributable material may need to remain under the same license family.")
    if noncommercial_only:
        restrictive_flags.append("noncommercial")
        redistribution_notes.append("Derived redistributable material may be limited to noncommercial use.")
    if any(s.excluded_from_upstream_license for s in inventory.sources):
        restrictive_flags.append("excluded-third-party-content")
        redistribution_notes.append("Some source-linked assets were flagged as excluded from the upstream course license.")

    return PackComplianceManifest(
        pack_id=pack_id,
        display_name=display_name,
        derived_from_sources=[s.source_id for s in inventory.sources],
        attribution_required=True,
        share_alike_required=share_alike_required,
        noncommercial_only=noncommercial_only,
        restrictive_flags=restrictive_flags,
        redistribution_notes=redistribution_notes,
    )

def compliance_qa(inventory: SourceInventory, manifest: PackComplianceManifest) -> dict:
    warnings: list[str] = []

    for src in inventory.sources:
        if not src.url:
            warnings.append(f"Source '{src.source_id}' is missing a URL.")
        if not src.license_id:
            warnings.append(f"Source '{src.source_id}' is missing a license identifier.")
        if src.license_id and not src.license_url:
            warnings.append(f"Source '{src.source_id}' is missing a license URL.")
        if not src.attribution_text:
            warnings.append(f"Source '{src.source_id}' is missing attribution text.")
        if src.excluded_from_upstream_license and not src.exclusion_notes:
            warnings.append(f"Source '{src.source_id}' is marked excluded but has no exclusion notes.")

    if manifest.attribution_required and not inventory.sources:
        warnings.append("Manifest requires attribution but the source inventory is empty.")

    if manifest.share_alike_required and "share-alike" not in manifest.restrictive_flags:
        warnings.append("Manifest indicates share-alike but restrictive flags are incomplete.")

    if manifest.noncommercial_only and "noncommercial" not in manifest.restrictive_flags:
        warnings.append("Manifest indicates noncommercial-only but restrictive flags are incomplete.")

    return {
        "warnings": warnings,
        "summary": {
            "warning_count": len(warnings),
            "source_count": len(inventory.sources),
            "share_alike_required": manifest.share_alike_required,
            "noncommercial_only": manifest.noncommercial_only,
        },
    }

def write_manifest(manifest: PackComplianceManifest, outpath: str | Path) -> None:
    Path(outpath).write_text(json.dumps(manifest.model_dump(), indent=2), encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser(description="Build and QA Didactopus course-ingestion compliance artifacts.")
    parser.add_argument("sources")
    parser.add_argument("--pack-id", default="demo-pack")
    parser.add_argument("--display-name", default="Demo Pack")
    parser.add_argument("--out", default="pack_compliance_manifest.json")
    args = parser.parse_args()

    inventory = load_sources(args.sources)
    manifest = build_pack_compliance_manifest(args.pack_id, args.display_name, inventory)
    qa = compliance_qa(inventory, manifest)
    write_manifest(manifest, args.out)
    print(json.dumps({"manifest": manifest.model_dump(), "qa": qa}, indent=2))

if __name__ == "__main__":
    main()
