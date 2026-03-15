# Working With Other MIT OCW Courses

This is the recommended pattern for bringing more MIT OpenCourseWare courses into Didactopus.

## Goal

Use MIT OCW as a structured source for learning, while preserving:

- attribution
- license references
- adaptation status
- noncommercial/share-alike flags
- a place to record excluded third-party content when it appears

## Minimal workflow

1. Pick a course and collect the specific pages you are actually using.
2. Create a local derived source file for reproducible ingestion.
3. Create a `sources.yaml` inventory beside that source file.
4. Run the ingestion/demo pipeline and emit a `pack_compliance_manifest.json`.
5. Review the generated pack before treating it as reusable teaching material.

## Recommended directory shape

For a new MIT OCW-derived example, mirror the existing pattern:

```text
examples/<course-slug>/
  course-source.md
  sources.yaml
```

The corresponding generated outputs should include:

```text
domain-packs/<course-slug>/
  license_attribution.json
  pack_compliance_manifest.json
  source_inventory.yaml
```

## What goes in `sources.yaml`

Record each course page or resource page that materially informed the generated pack.

At minimum include:

- `source_id`
- `title`
- `url`
- `publisher`
- `creator`
- `license_id`
- `license_url`
- `retrieved_at`
- `adapted`
- `attribution_text`
- `excluded_from_upstream_license`
- `exclusion_notes`

Use `examples/ocw-information-entropy/sources.yaml` as the concrete model.

## When to add excluded-source records

Add explicit excluded records when:

- the course page points to third-party figures or readings
- the page itself warns that a particular asset is excluded from the main course license
- you want the record preserved even though you do not reuse the asset

That is the route for acknowledging future sources that require special handling.

## Practical advice for course selection

Good first OCW candidates:

- courses with a strong week-by-week or unit-by-unit structure
- courses with stable textual descriptions, readings, or assignments
- courses where you can summarize the progression into a single local source file

Harder candidates:

- courses whose value is mostly in embedded media
- courses with many third-party handouts or linked readings
- courses with weak textual structure

## Current repo reference

The MIT OCW Information and Entropy demo is the reference implementation of this pattern:

- source file: `examples/ocw-information-entropy/6-050j-information-and-entropy.md`
- source inventory: `examples/ocw-information-entropy/sources.yaml`
- generated pack: `domain-packs/mit-ocw-information-entropy/`
