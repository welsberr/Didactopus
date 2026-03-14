# Didactopus Object Editing, Versioning, Merge/Apply, and Export Layer

This layer extends promotion target objects with:

- editable downstream objects
- version history for promoted objects
- merge/apply flow for pack patch proposals
- export formats for curriculum drafts and skill bundles

It adds concrete scaffolding for turning promoted outputs into maintainable assets
rather than one-off records.

## Added capabilities

- versioned pack patch proposals
- versioned curriculum drafts
- versioned skill bundles
- patch-apply endpoint for updating pack JSON
- markdown/json export for curriculum drafts
- json/yaml-style manifest export for skill bundles
- reviewer UI prototype for editing and exporting target objects

## Why this matters

A promotion target is only the start of the lifecycle. Real use requires:

- revision
- comparison
- approval
- application
- export

This scaffold establishes those mechanisms in a minimal but extensible form.
