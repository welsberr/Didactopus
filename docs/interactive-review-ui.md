# Interactive Review UI

The review UI is the local-first front end for inspecting and promoting draft packs.

## What the current code supports

The UI is backed by a JSON review model and a local bridge server.

Key files and modules:

- `webui/`
- `didactopus.review_schema`
- `didactopus.review_loader`
- `didactopus.review_actions`
- `didactopus.review_export`
- `didactopus.review_bridge`
- `didactopus.review_bridge_server`

## Data flow

1. A draft pack is loaded into a review session.
2. The review bridge serves workspace and session data.
3. The frontend consumes `review_data.json`-style payloads.
4. Review actions update concept status, notes, and prerequisites.
5. The promoted pack export writes reviewed pack files and a review ledger.

## Current feature set

- concept list and detail views
- editable concept status
- note editing
- prerequisite editing
- save/load via the review bridge
- export of promoted pack artifacts
- workspace create/open/import support through the bridge server

## Outputs

The review export layer currently writes:

- `review_session.json`
- `review_data.json`
- promoted `pack.yaml`
- promoted `concepts.yaml`
- `review_ledger.json`
- `license_attribution.json`

## Limits

- the UI remains local-first and file-backed
- merge/split concept actions are not deeply modeled yet
- richer diff and conflict tooling is still future work
