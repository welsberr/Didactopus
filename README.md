# Didactopus

![Didactopus mascot](artwork/didactopus-mascot.png)

Didactopus is a local-first Python codebase for turning educational source material into structured learning domains, evaluating learner progress against those domains, and exporting review, mastery, and skill artifacts.

At a high level, the repository does five things:

1. Ingest source material such as Markdown, text, HTML, PDF-ish text, DOCX-ish text, and PPTX-ish text into normalized course/topic structures.
2. Distill those structures into draft domain packs with concepts, prerequisites, roadmaps, projects, attribution, and review flags.
3. Validate, review, and promote those draft packs through a workspace-backed review flow.
4. Build merged learning graphs, rank next concepts, accumulate learner evidence, and export capability profiles.
5. Demonstrate end-to-end flows, including an MIT OCW Information and Entropy demo that produces a pack, learner outputs, a reusable skill bundle, and progress visualizations.

## What Is In This Repository

- `src/didactopus/`
  The application and library code.
- `tests/`
  The automated test suite.
- `domain-packs/`
  Example and generated domain packs.
- `examples/`
  Sample source inputs and generated outputs.
- `skills/`
  Repo-local skill bundles generated from knowledge products.
- `webui/`
  A local review/workbench frontend scaffold.
- `docs/`
  Focused design and workflow notes.

## Core Workflows

### 1. Course and topic ingestion

The ingestion path converts source documents into `NormalizedDocument`, `NormalizedCourse`, and `TopicBundle` objects, then emits a draft pack.

Main modules:

- `didactopus.document_adapters`
- `didactopus.course_ingest`
- `didactopus.topic_ingest`
- `didactopus.rule_policy`
- `didactopus.pack_emitter`

Primary outputs:

- `pack.yaml`
- `concepts.yaml`
- `roadmap.yaml`
- `projects.yaml`
- `rubrics.yaml`
- `review_report.md`
- `conflict_report.md`
- `license_attribution.json`

### 2. Review and workspace management

Draft packs can be brought into review workspaces, edited, and promoted to reviewed packs.

Main modules:

- `didactopus.review_schema`
- `didactopus.review_loader`
- `didactopus.review_actions`
- `didactopus.review_export`
- `didactopus.workspace_manager`
- `didactopus.review_bridge`
- `didactopus.review_bridge_server`

Key capabilities:

- create and list workspaces
- preview draft-pack imports
- import draft packs with overwrite checks
- save review actions
- export promoted packs
- export `review_data.json` for the frontend

### 3. Learning graph and planning

Validated packs can be merged into a namespaced DAG, including explicit overrides and stage/project catalogs.

Main modules:

- `didactopus.artifact_registry`
- `didactopus.learning_graph`
- `didactopus.graph_builder`
- `didactopus.concept_graph`
- `didactopus.planner`
- `didactopus.adaptive_engine`

Key capabilities:

- dependency validation for packs
- merged prerequisite DAG construction
- roadmap generation from merged stages
- graph-aware next-concept ranking
- adaptive plan generation from current mastery

### 4. Evidence, mastery, and capability export

Learner progress is represented as evidence summaries plus exported capability artifacts.

Main modules:

- `didactopus.evidence_engine`
- `didactopus.evaluator_pipeline`
- `didactopus.progression_engine`
- `didactopus.mastery_ledger`
- `didactopus.knowledge_export`

Key capabilities:

- weighted evidence ingestion
- confidence estimation
- multidimensional mastery checks
- resurfacing weak concepts
- capability profile JSON export
- markdown capability reports
- artifact manifests

### 5. Agentic learner demos and visualization

The repository includes deterministic agentic demos rather than a live external model integration.

Main modules:

- `didactopus.agentic_loop`
- `didactopus.ocw_information_entropy_demo`
- `didactopus.ocw_progress_viz`

Generated demo artifacts:

- `domain-packs/mit-ocw-information-entropy/`
- `examples/ocw-information-entropy-run/`
- `skills/ocw-information-entropy-agent/`

## Quick Start

### Install

```bash
pip install -e .
```

### Run tests

```bash
pytest
```

### Generate the MIT OCW demo pack, learner outputs, and skill bundle

```bash
python -m didactopus.ocw_information_entropy_demo
```

This writes:

- `domain-packs/mit-ocw-information-entropy/`
- `examples/ocw-information-entropy-run/`
- `skills/ocw-information-entropy-agent/`

### Render learner progress visualizations

Path-focused view:

```bash
python -m didactopus.ocw_progress_viz
```

Full concept map including noisy non-path concepts:

```bash
python -m didactopus.ocw_progress_viz --full-map
```

### Run the review bridge server

```bash
python -m didactopus.review_bridge_server
```

The default config file is `configs/config.example.yaml`.

## Current State

This repository is functional, but parts of it remain intentionally heuristic.

What is solid:

- pack validation and dependency checks
- review-state export and workspace import flow
- merged learning graph construction
- weighted evidence and capability exports
- deterministic agentic demo runs
- generated skill bundles and progress visualizations

What remains heuristic or lightweight:

- document adapters for binary formats are simplified text adapters
- concept extraction can produce noisy candidate terms
- evaluator outputs are heuristic rather than formal assessments
- the agentic learner loop uses synthetic attempts
- the frontend and bridge flow are local-first scaffolds, not a hosted product

## Recommended Reading

- [docs/course-to-pack.md](docs/course-to-pack.md)
- [docs/learning-graph.md](docs/learning-graph.md)
- [docs/agentic-learner-loop.md](docs/agentic-learner-loop.md)
- [docs/mastery-ledger.md](docs/mastery-ledger.md)
- [docs/workspace-manager.md](docs/workspace-manager.md)
- [docs/interactive-review-ui.md](docs/interactive-review-ui.md)
- [docs/faq.md](docs/faq.md)

## MIT OCW Demo Notes

The MIT OCW Information and Entropy demo is grounded in the MIT OpenCourseWare course page and selected unit/readings metadata, then converted into a local course source file for reproducible ingestion. The resulting generated pack and learner outputs are intentionally reviewable rather than presented as authoritative course mirrors.
