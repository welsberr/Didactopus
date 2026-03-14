# Didactopus Review Governance Layer

This update extends the admin-curation scaffold with a **review and governance layer**
for contributed and curated packs.

## Added in this scaffold

- pack versioning records
- draft / in_review / approved / rejected publication states
- reviewer comments and sign-off records
- moderation workflow for contributed packs
- admin UI views for governance and review history

## Why this matters

Once Didactopus accepts contributed packs or substantial revisions, it needs more than
editing and inspection. It needs process.

A governance-capable system should let maintainers:
- see what version of a pack is current
- review proposed updates before publication
- record reviewer comments
- approve or reject submissions explicitly
- preserve an audit trail of those actions

## Scope

This remains a scaffold:
- versioning is simple and linear
- moderation states are explicit but minimal
- audit history is prototype-level
- approval logic is not yet policy-driven

## Strong next step

- connect governance to the full QA pipeline
- require validation/provenance checks before approval
- add multi-reviewer policies and required approvals
- support diff views between pack versions
