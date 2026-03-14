# Draft-Pack Import Workflow

The draft-pack import workflow bridges ingestion output and review workspace setup.

## Why it exists

Without import support, users still have to manually:
- locate a generated draft pack
- create a workspace
- copy files into the right directory
- reopen the review tool

That is exactly the kind of startup friction Didactopus is supposed to reduce.

## Current scaffold

This revision adds:
- import API endpoint
- workspace-manager copy/import operation
- UI controls for creating a workspace and importing a draft pack path

## Import behavior

The current scaffold:
- creates the target workspace if needed
- copies the source draft-pack directory into `workspace/draft_pack/`
- updates workspace metadata
- allows the workspace to be opened immediately afterward

## Future work

- file picker integration
- import validation
- overwrite protection / confirmation
- pack schema validation before import
- duplicate import detection
