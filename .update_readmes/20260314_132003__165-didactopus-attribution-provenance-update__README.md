# Didactopus

This update adds an **attribution, provenance, and license-compliance scaffold** for domain packs.

It is designed for open-courseware ingestion workflows, including sources such as MIT OpenCourseWare,
where downstream reuse may be allowed but requires preserving provenance and meeting license terms.

## Why this matters

A Didactopus domain pack should not be a black box. If source materials contributed to the pack,
the pack should carry machine-readable and human-readable provenance so that:
- attribution can be generated automatically
- remix/adaptation status can be recorded
- excluded third-party content can be flagged
- downstream redistribution can be audited more safely
- human learners and maintainers can inspect where content came from

## Included in this update

- source provenance models
- attribution bundle generator
- attribution QA checks
- sample `sources.yaml`
- sample `ATTRIBUTION.md`
- pack-level provenance manifest
- MIT OCW-oriented notes for compliance-aware ingestion

## Pack artifacts introduced here

- `sources.yaml` — source inventory and licensing metadata
- `ATTRIBUTION.md` — human-readable attribution report
- `provenance_manifest.json` — machine-readable normalized provenance output

## Important note

This scaffold helps operationalize attribution and provenance handling.
It is **not** legal advice.
