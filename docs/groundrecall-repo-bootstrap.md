# GroundRecall Repo Bootstrap Checklist

This document turns the broader [groundrecall-migration-plan.md](groundrecall-migration-plan.md) into a practical checklist for creating a standalone `GroundRecall` repository.

The goal here is narrower than full feature completion. The goal is to get to a standalone repository that can be installed, run locally, and used for real `llmwiki++`-style work without requiring `Didactopus` as the primary shell.

## Bootstrap Goal

Minimum viable standalone `GroundRecall` repo:

- installable as its own Python package
- exposes a first-class `groundrecall` CLI
- imports and normalizes knowledge sources
- promotes reviewed knowledge into a canonical store
- supports query and export over promoted state
- supports assistant-neutral exports plus adapter exports
- remains consumable by `Didactopus` as a dependency or sibling package

This is enough for a local standalone alpha. It is not yet the full distributed team and corpus-scale vision.

## What Already Exists

The current `Didactopus` codebase already contains most of the implementation spine:

- `didactopus.groundrecall.ingest`
- `didactopus.groundrecall.source_adapters.*`
- `didactopus.groundrecall.models`
- `didactopus.groundrecall.store`
- `didactopus.groundrecall.promotion`
- `didactopus.groundrecall.query`
- `didactopus.groundrecall.export`
- `didactopus.groundrecall.assistant_export`
- `didactopus.groundrecall.assistants.*`
- `didactopus.groundrecall.inspect`
- `didactopus.groundrecall.cli`

This means the repo bootstrap is primarily a packaging and boundary exercise, not a greenfield implementation.

## Target Repo Shape

Suggested standalone layout:

```text
groundrecall/
  pyproject.toml
  README.md
  LICENSE
  src/
    groundrecall/
      __init__.py
      cli.py
      ingest.py
      inspect.py
      lint.py
      models.py
      store.py
      promotion.py
      query.py
      export.py
      assistant_export.py
      review_queue.py
      review_bridge.py
      source_adapters/
      assistants/
  tests/
  docs/
    quickstart.md
    llmwiki-import.md
    deployment-modes.md
    assistant-architecture.md
    sync-roadmap.md
```

Notes:

- `review_bridge.py` may remain optional if the standalone repo only needs generic review artifacts.
- `review_queue.py` belongs in `GroundRecall`; it is not a learner-only concern.
- `review_bridge.py` is the most likely file to stay transitional if it depends too directly on Didactopus review objects.

## Move / Keep / Bridge

### Move into standalone `GroundRecall`

Move first:

- `didactopus.groundrecall.ingest`
- `didactopus.groundrecall.inspect`
- `didactopus.groundrecall.lint`
- `didactopus.groundrecall.models`
- `didactopus.groundrecall.store`
- `didactopus.groundrecall.promotion`
- `didactopus.groundrecall.query`
- `didactopus.groundrecall.export`
- `didactopus.groundrecall.assistant_export`
- `didactopus.groundrecall.review_queue`
- `didactopus.groundrecall.source_adapters.*`
- `didactopus.groundrecall.assistants.*`
- `didactopus.groundrecall.cli`

### Keep in `Didactopus`

These should not move:

- learner session and mentor/practice flows
- educational pack authoring and pack-specific UX
- mastery/evidence learner experiences
- provider demos that exist to support Didactopus learner workflows

### Keep as temporary bridges

These may need a staged treatment:

- `groundrecall_review_bridge`
- `didactopus_pack` source adapter

Those are useful during transition, but they are cross-boundary integrations, not proof that `GroundRecall` must remain inside `Didactopus`.

## Bootstrap Checklist

### 1. Create the new repo skeleton

Required:

- create a new repo root
- add `pyproject.toml`
- add `src/groundrecall/`
- add `tests/`
- add `docs/`
- add a minimal `README.md`
- add `LICENSE`

Definition of done:

- `pip install -e .` works
- `python -m groundrecall.cli --help` works

### 2. Move the package code

Required:

- copy the current `didactopus.groundrecall.*` package into `src/groundrecall/`
- update relative imports as needed
- remove `didactopus`-prefixed assumptions in docstrings and parser help text

Definition of done:

- module imports succeed under `groundrecall.*`
- no package file requires `didactopus` imports except explicit transition bridges

### 3. Extract the tests

Required:

- move GroundRecall-focused tests into the new repo
- keep Didactopus integration tests in Didactopus
- add an end-to-end CLI smoke test that runs:
  - `import`
  - `promote`
  - `query`
  - `export`
  - `inspect`

Definition of done:

- the new repo has its own passing test suite
- Didactopus retains only integration tests that prove interoperability

### 4. Harden the standalone CLI

Required commands:

- `groundrecall import`
- `groundrecall lint`
- `groundrecall promote`
- `groundrecall query`
- `groundrecall export`
- `groundrecall inspect`

Recommended additions:

- `groundrecall assistant-export`
- `groundrecall review-queue`

Definition of done:

- the CLI help text is standalone and does not refer users back to `Didactopus`

### 5. Publish a repo-local data layout

Pick and document a stable layout such as:

```text
.groundrecall/
  imports/
  store/
  exports/
  events/
```

Required:

- make these paths configurable
- define sane defaults
- remove assumptions that the caller already knows the Didactopus workspace layout

Definition of done:

- a new user can run GroundRecall in an empty directory and get predictable local state

### 6. Document the standalone workflows

At minimum:

- quickstart
- migrate from `llmwiki`
- query and export patterns
- assistant adapter exports
- relationship to `Didactopus`
- relationship to `GenieHive`

Definition of done:

- the README can orient a new user without requiring Didactopus-specific context

### 7. Leave compatibility shims in `Didactopus`

Required:

- keep thin wrappers at `didactopus.groundrecall_*` or `didactopus.groundrecall.*` integration paths as needed
- make `Didactopus` import the extracted package where possible
- clearly mark the wrappers as compatibility paths

Definition of done:

- existing Didactopus workflows do not break during the split

## Alpha Completion Criteria

The standalone repo is alpha-ready when:

- `llmwiki` import works
- `markdown_notes` import works
- at least one Didactopus-native adapter still works as an integration adapter
- canonical store creation and snapshot export work
- query works over promoted objects
- assistant-neutral export works
- at least two assistant adapters export usable bundles

This is the right threshold for “functional GroundRecall repo.”

## Still Missing After Alpha

A standalone alpha is not yet the full target system. These remain post-bootstrap priorities:

- re-import and update semantics
- append-only event logs for multi-node merge
- shared/private scope support
- merge and sync conflict handling
- stronger claim extraction
- richer claim-level review and adjudication
- corpus-scale distributed coordination

Those features should be built in `GroundRecall`, but they do not need to block repo extraction.

## Recommended Execution Order

Use this order:

1. create the repo and package skeleton
2. copy the current `groundrecall` package and make imports pass
3. move tests and get the standalone suite green
4. finalize CLI and README
5. switch Didactopus integration points to consume the extracted package
6. only then continue with sync/merge and corpus-scale features

This keeps the boundary clean without stalling feature progress.

## First PR-Sized Steps

If this were executed as concrete work, the first three small changes should be:

1. create the new repo with package skeleton and copy `src/didactopus/groundrecall/`
2. move the existing namespace-focused tests and make them pass under `groundrecall.*`
3. add a standalone README quickstart and one end-to-end CLI smoke test

After that, the repo is real enough to iterate in place rather than continuing to plan around it.
