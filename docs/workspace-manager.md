# Workspace Manager

The workspace manager organizes review work around draft packs.

## Why it exists

Without a workspace layer, users have to manually track:

- generated draft-pack directories
- which draft is currently active in review
- where review exports belong
- whether an import would overwrite existing work

The current code reduces that friction by giving review work a registry and import lifecycle.

## Current implementation

`didactopus.workspace_manager.WorkspaceManager` currently supports:

- `create_workspace(...)`
- `list_workspaces()`
- `get_workspace(...)`
- `touch_recent(...)`
- `preview_import(...)`
- `import_draft_pack(...)`

The registry is stored as JSON and the default workspace root is configurable through `configs/config.example.yaml`.

## Import behavior

Draft-pack import currently:

- validates source-pack availability through preview logic
- reports whether overwrite will be required
- creates the target workspace if needed
- copies the source draft pack into `workspace/draft_pack/`
- updates registry metadata and recency ordering

If the target workspace already exists, import requires `allow_overwrite=True`.

## Bridge integration

The review bridge server exposes workspace operations through local HTTP endpoints, including:

- list workspaces
- create workspace
- open workspace
- import preview
- import draft pack

These endpoints are used to connect ingestion outputs to the review workflow without manual file shuffling.
