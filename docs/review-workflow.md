# Review Workflow

The Didactopus review workflow sits between draft-pack generation and trusted pack use.

## Why it exists

Automated ingestion is useful, but draft packs are not reliable enough to trust blindly.
Human curation is needed to:

- fix mistaken prerequisite edges
- merge duplicate or near-duplicate concepts
- split over-broad concepts
- remove weak concept candidates
- classify concepts by trust level
- resolve terminology conflicts

## Workflow stages

1. load draft pack
2. inspect concepts, prerequisites, conflicts, and review flags
3. apply curation actions
4. record rationale in a review ledger
5. generate promoted pack
6. preserve provenance

## Trust statuses

Current scaffold statuses:
- `trusted`
- `provisional`
- `rejected`
- `needs_review`

## Promotion

Promotion does not erase provenance.
The promoted pack keeps:
- curation metadata
- source attribution
- review ledger
- timestamps and reviewer identity fields
