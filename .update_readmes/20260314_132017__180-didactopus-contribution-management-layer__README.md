# Didactopus Contribution Management Layer

This update extends the review-governance scaffold with a **contribution management layer**.

## Added in this scaffold

- contributor submission records
- pack diffs between versions
- approval gates tied to validation/provenance status
- reviewer task queue / notification scaffold
- admin UI views for submissions, diffs, and review tasks

## Why this matters

Once Didactopus supports outside contributors, maintainers need a structured way to:
- receive submissions
- compare proposed revisions against current versions
- see whether QA/provenance gates are satisfied
- assign or at least surface review work
- keep an audit trail of what was submitted and why it was accepted or rejected

## Scope

This remains a scaffold:
- diffs are summary-oriented rather than line-perfect
- notification/task queues are prototype records
- gate checks are simple but explicit
- contributor identity is tied to existing users rather than a separate contributor model

## Strong next step

- richer semantic diffs for concepts/onboarding/compliance
- required reviewer assignment rules
- notifications via email/chat connectors
- policy engine for gating approvals
