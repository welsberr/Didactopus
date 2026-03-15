# Course-Ingestion Compliance Notes

Didactopus domain packs may be derived from licensed educational sources.
That means the ingestion pipeline should preserve enough information to support:

- attribution
- license URL retention
- adaptation status
- share-alike / noncommercial flags
- explicit exclusion handling for third-party content
- downstream auditability

## Recommended source record fields

Each ingested source should carry:
- source ID
- title
- URL
- publisher
- creator
- license ID
- license URL
- retrieval date
- adaptation flag
- attribution text
- exclusion flag
- exclusion notes

## Pack-level compliance fields

A derived pack should carry:
- derived_from_sources
- restrictive_flags
- redistribution_notes
- attribution_required
- share_alike_required
- noncommercial_only

The recommended route in this repository is:

1. maintain a `sources.yaml` inventory for the source set
2. generate `pack_compliance_manifest.json`
3. keep `license_attribution.json` for human-facing attribution details

## MIT OCW-specific pattern

For MIT OpenCourseWare-derived packs, treat the course material as licensed content while separately recording:
- third-party exclusions
- image/video exceptions
- linked-content exceptions
- any asset not safely covered by the course-level reuse assumption

The MIT OCW Information and Entropy demo in this repository follows that pattern and can be used as the reference implementation.
