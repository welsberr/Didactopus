# GroundRecall Migration Plan

This document turns the boundary decisions in [deployment-modes.md](deployment-modes.md) into an implementation plan.

The goal is not an immediate repo split. The goal is to let `GroundRecall` become independently deployable and operable without destabilizing ongoing `Didactopus` learner work.

## Current State

Today, GroundRecall exists as a set of modules under `src/didactopus/`:

- `groundrecall_import`
- `groundrecall_source_adapters/*`
- `groundrecall_lint`
- `groundrecall_review_queue`
- `groundrecall_review_bridge`
- `groundrecall_models`
- `groundrecall_store`
- `groundrecall_promotion`
- `groundrecall_query`
- `groundrecall_export`
- `groundrecall_assistant_export`
- `groundrecall_assistants/*`

This is acceptable as an implementation phase, but it creates two risks:

1. generic knowledge-substrate functionality may continue to accrete under `didactopus.main`
2. feature work may silently assume the presence of learner-facing Didactopus components

## Migration Goal

Target state:

- `Didactopus` remains the learner-facing application
- `GroundRecall` becomes the standalone grounded knowledge substrate
- `GenieHive` remains the model and routing control plane

The package, CLI, and deployment boundaries should eventually reflect that.

## Target Ownership

### GroundRecall should own

- source ingestion and normalization
- claim/concept/relation/artifact/provenance schemas
- canonical store and snapshots
- lint and review queue generation
- promotion and merge semantics
- assistant-neutral query and export
- assistant adapter export
- sync, merge, and team/shared knowledge operations

### Didactopus should own

- learner session flows
- mentor/practice/evaluator/project-advisor workflows
- pack and curriculum-specific review UX
- mastery-ledger and learner evidence experiences
- educational packaging over grounded knowledge

### Shared boundary helpers should stay narrow

- provider policy that depends on GenieHive route resolution but serves learner workflows
- review bridges where GroundRecall needs to feed an existing Didactopus review process during the transition

## Packaging Direction

### Phase 0: Present layout, stricter discipline

Keep the code in `src/didactopus/`, but use naming and imports that preserve the eventual split.

Rules:

- new generic knowledge features go into `groundrecall_*` modules
- new learner-facing features go into `didactopus` learner modules
- do not add generic knowledge operations to `didactopus.main`
- treat review bridges as bridges, not permanent core ownership

### Phase 1: Explicit namespace inside the repo

Preferred direction:

- move GroundRecall modules under `src/didactopus/groundrecall/`

Target structure:

- `src/didactopus/groundrecall/ingest.py`
- `src/didactopus/groundrecall/source_adapters/`
- `src/didactopus/groundrecall/models.py`
- `src/didactopus/groundrecall/store.py`
- `src/didactopus/groundrecall/promotion.py`
- `src/didactopus/groundrecall/query.py`
- `src/didactopus/groundrecall/export.py`
- `src/didactopus/groundrecall/assistants/`
- `src/didactopus/groundrecall/sync.py`
- `src/didactopus/groundrecall/merge.py`
- `src/didactopus/groundrecall/cli.py`

Benefits:

- cleaner conceptual grouping
- easier extraction later
- clearer import discipline

Compatibility path:

- keep thin wrapper modules at old import paths during transition
- deprecate wrappers only after tests and docs have moved

### Phase 2: Dual CLI identity

Before any repo split, expose GroundRecall as a first-class CLI namespace.

Desired commands:

- `python -m didactopus.groundrecall.cli import ...`
- `python -m didactopus.groundrecall.cli lint ...`
- `python -m didactopus.groundrecall.cli promote ...`
- `python -m didactopus.groundrecall.cli query ...`
- `python -m didactopus.groundrecall.cli export ...`
- `python -m didactopus.groundrecall.cli inspect ...`

At that point, `didactopus.main` should only surface:

- learner-facing commands
- review-workflow commands with educational intent
- possibly a pointer to GroundRecall commands, but not ownership of them

### Phase 3: Optional package extraction

Only after sync/merge and standalone use are mature:

- move GroundRecall to its own package or repo if that becomes operationally useful
- keep Didactopus consuming it as a dependency

This step is optional. A clean package boundary inside one repo may be sufficient for a long time.

## CLI Migration Plan

### Keep under `didactopus.main`

- `review`
- future learner-facing workbench commands

### Move toward GroundRecall CLI

- import
- lint
- review queue
- promotion
- canonical query
- canonical export
- assistant export
- sync and merge

### Transitional exception

`provider-inspect` can remain on the Didactopus umbrella CLI for now because:

- it is already useful operationally
- it supports learner-node deployments
- it is not a GroundRecall-specific operation

Longer term, it may also belong on a separate operator surface depending on whether Didactopus becomes the standard local application shell.

## Module Mapping

### Move first

Current -> target

- `didactopus.groundrecall_import` -> `didactopus.groundrecall.ingest`
- `didactopus.groundrecall_source_adapters.*` -> `didactopus.groundrecall.source_adapters.*`
- `didactopus.groundrecall_models` -> `didactopus.groundrecall.models`
- `didactopus.groundrecall_store` -> `didactopus.groundrecall.store`
- `didactopus.groundrecall_promotion` -> `didactopus.groundrecall.promotion`
- `didactopus.groundrecall_query` -> `didactopus.groundrecall.query`
- `didactopus.groundrecall_export` -> `didactopus.groundrecall.export`
- `didactopus.groundrecall_assistants.*` -> `didactopus.groundrecall.assistants.*`

### Keep as transitional bridges

- `didactopus.groundrecall_review_bridge`
- source adapters that ingest Didactopus-native artifacts

These are legitimate but should be documented as cross-boundary adapters rather than intrinsic ownership proof.

### Stay in Didactopus

- `learner_session`
- `learner_session_demo`
- `mentor`
- `practice`
- `project_advisor`
- educational review UX modules
- pack and graph-planning modules

## Service Boundary Direction

### GroundRecall service candidates

Once needed, a GroundRecall service should focus on:

- canonical knowledge query
- import status and queue inspection
- promotion status
- sync/merge status
- assistant-neutral bundle retrieval

### Didactopus service candidates

- learner session orchestration
- learner progress and evaluation
- pack/workbench interactions

### GenieHive service candidates

- model and service inspection
- route resolution
- cluster health

## Milestones

### Milestone 1: Namespace discipline

Done when:

- new generic knowledge work lands only in GroundRecall-oriented modules
- `didactopus.main` stops growing generic knowledge commands
- docs consistently describe GroundRecall as a substrate, not a learner feature

### Milestone 2: Internal package reorganization

Done when:

- GroundRecall modules live under an explicit package path
- old flat import paths are wrappers only
- tests target the new package paths

### Milestone 3: First-class GroundRecall CLI

Done when:

- import/lint/promote/query/export/inspect are available under one GroundRecall CLI surface
- operator docs no longer require `Didactopus` framing for generic knowledge tasks

### Milestone 4: Sync and merge maturity

Done when:

- append-only event ingestion exists
- promoted-state merge semantics exist
- team/shared knowledge workflows are practical without learner workflows

### Milestone 5: Extraction decision

Done when:

- the project can make an informed choice between:
  - one repo, multiple packages
  - separate GroundRecall package/repo

## Immediate Next Work

Recommended next implementation steps:

1. Introduce `didactopus.groundrecall` as an internal package namespace.
2. Add a single GroundRecall umbrella CLI module.
3. Keep thin wrapper modules for compatibility.
4. Start moving docs and tests to the new namespace.
5. Begin implementing sync/merge primitives under GroundRecall rather than under Didactopus learner flows.

## Decision Rule For New Work

Before adding a new command, module, or service, ask:

1. Would this still be needed if there were no learner session?
2. Would a team using only shared knowledge still need it?
3. Is the canonical artifact knowledge state or educational interaction?
4. Would it still matter if Didactopus UI vanished?

If yes, default toward GroundRecall.
