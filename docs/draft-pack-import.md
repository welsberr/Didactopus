# Draft-Pack Import Workflow

Draft-pack import connects ingestion output to the review workspace flow.

## Current behavior

The import path currently supports:

- import preview through `preview_draft_pack_import(...)`
- overwrite detection before import
- workspace creation when the target workspace does not exist yet
- copying the source pack into `workspace/draft_pack/`
- workspace-recency updates after import

## Main modules

- `didactopus.import_validator`
- `didactopus.workspace_manager`
- `didactopus.review_bridge_server`

## Bridge endpoints

The bridge server exposes:

- `/api/workspaces/import-preview`
- `/api/workspaces/import`

These endpoints return structured success/error payloads for missing source directories, invalid source packs, or overwrite conflicts.

## Why it matters

The import flow removes a manual step between "I generated a draft pack" and "I can now review it in a managed workspace."
