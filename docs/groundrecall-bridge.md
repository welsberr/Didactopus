# GroundRecall Bridge

This documents the smallest end-to-end path for carrying reviewed
`GroundRecall` concept context into a `Didactopus` draft pack.

## Purpose

Use this when:

- the source material began as legacy office documents
- `doclift` has already normalized those documents into a bundle
- `GroundRecall` already contains a reviewed concept you want to carry into the
  learner-facing pack as grounded context

The bridge does not replace `Didactopus` pack generation. It enriches it with a
pack-ready `groundrecall_query_bundle.json` artifact.

## Inputs

You need:

1. a `GroundRecall` canonical store directory
2. a concept reference resolvable in that store
3. a `doclift` bundle directory
4. an output directory for the generated `Didactopus` pack

## Command

```bash
didactopus doclift-bundle-groundrecall \
  /path/to/groundrecall-store \
  channel-capacity \
  /tmp/doclift-bundle \
  /tmp/didactopus-pack \
  --course-title "Example Course"
```

Arguments:

- `groundrecall_store_dir`: canonical GroundRecall store
- `groundrecall_concept_ref`: concept id, short id, or matching concept text
- `bundle_dir`: `doclift` bundle root
- `pack_dir`: output directory for the generated pack
- `--course-title`: display title for the generated pack

Optional:

- `--author`
- `--license-name`

## What It Does

The command performs four steps:

1. exports a pack-ready `groundrecall_query_bundle.json` from the GroundRecall store
2. places that artifact in a temporary `_groundrecall` area under the target pack
3. runs the normal `doclift` bundle demo pack generation flow
4. writes the resulting pack with `groundrecall_query_bundle.json` included as a declared supporting artifact

## Outputs

The generated pack directory contains the normal `Didactopus` draft-pack files,
plus:

- `groundrecall_query_bundle.json`
- `doclift_bundle_summary.json`

The pack summary also records:

- `groundrecall_bundle_included`
- `groundrecall_concept_ref`
- `groundrecall_query_bundle_path`

## Why This Matters

This bridge keeps the responsibilities distinct:

- `doclift` normalizes documents
- `GroundRecall` stores canonical reviewed concept context
- `Didactopus` builds learner-facing packs and workbench flows

But it removes the manual handoff step where a user previously had to export
and place `groundrecall_query_bundle.json` by hand.

## Related Commands

Export the pack-ready query bundle directly from GroundRecall:

```bash
python -m groundrecall.export /path/to/groundrecall-store /tmp/groundrecall-export \
  --pack-ready-concept channel-capacity
```

Run the plain `doclift` bundle conversion without GroundRecall:

```bash
didactopus doclift-bundle /tmp/doclift-bundle /tmp/didactopus-pack --course-title "Example Course"
```

Build just the Notebook page artifact from a GroundRecall concept:

```bash
didactopus notebook-page-groundrecall \
  /path/to/groundrecall-store \
  channel-capacity \
  /tmp/notebook-page-export
```
