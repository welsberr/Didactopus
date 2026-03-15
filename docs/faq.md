# FAQ

## What is Didactopus, in one sentence?

Didactopus turns educational material into structured learning packs, then uses graphs, evidence, and review workflows to support human or AI learning against those packs.

## Is this a packaged application or a research/workbench repository?

It is a workbench-style repository with runnable code, tests, example packs, generated outputs, and local-first review/demo flows.

## What is a domain pack?

A domain pack is the unit Didactopus uses to represent a learning domain. In practice it is a directory containing:

- `pack.yaml`
- `concepts.yaml`
- `roadmap.yaml`
- `projects.yaml`
- `rubrics.yaml`

Generated packs may also include review, conflict, and attribution artifacts.

## What is the difference between a draft pack and a reviewed pack?

A draft pack is an ingestion output. A reviewed pack is a pack that has been loaded into the review workflow, edited or triaged by a reviewer, and exported again with review metadata applied.

## What does the workspace manager do?

It keeps review work organized. The current implementation supports:

- create workspace
- list workspaces
- touch/open recent workspaces
- preview draft-pack import
- import draft packs into `workspace/draft_pack/`
- overwrite checks before replacing an existing draft pack

## Does Didactopus really ingest PDF, DOCX, and PPTX files?

Yes, but conservatively. Those adapters currently normalize text in a simplified way. They exist to stabilize the interface and surrounding workflow rather than to claim production-grade document parsing.

## Does the agentic learner call an external LLM?

No. The current agentic learner paths are deterministic and synthetic. They are meant to exercise the orchestration pattern, evaluator pipeline, mastery updates, capability export, and visualization flow without requiring an external model service.

## What is the current evidence model?

The evidence engine supports:

- evidence items grouped by concept
- per-type weighting
- optional recency weighting
- confidence derived from accumulated evidence mass
- dimension-level summaries
- resurfacing when recent weak evidence drags mastery below threshold

## What does the capability export contain?

The exported capability profile includes:

- learner identity
- target domain
- mastered concepts
- weak dimensions by concept
- evaluator summaries by concept
- artifact records

The main export formats are JSON, Markdown, and an artifact manifest.

## What is the MIT OCW Information and Entropy demo?

It is the repo's current end-to-end reference flow. Running:

```bash
python -m didactopus.ocw_information_entropy_demo
```

generates:

- a new pack in `domain-packs/mit-ocw-information-entropy/`
- learner outputs in `examples/ocw-information-entropy-run/`
- a repo-local skill bundle in `skills/ocw-information-entropy-agent/`

## What visualizations exist today?

The OCW demo currently generates two visualization modes:

- a guided-path learner progress view
- a full concept map that also surfaces noisy non-path concepts

You can render them with:

```bash
python -m didactopus.ocw_progress_viz
python -m didactopus.ocw_progress_viz --full-map
```

## Is the generated content free of extractor noise?

No. The current extractors can still emit noisy candidate concepts, especially from title-cased phrases embedded in lesson text. That is why review flags, workspace review, and promotion flows are first-class parts of the project.

## How should I think about validation versus QA?

Validation is structural: required files, schemas, references, duplicates, dependencies.

QA is heuristic: coverage alignment, evaluator alignment, path quality, semantic QA, and related diagnostics that try to surface likely quality problems before or during review.

## Where should I start reading if I want the full project overview?

Start with:

- `README.md`
- `docs/course-to-pack.md`
- `docs/learning-graph.md`
- `docs/mastery-ledger.md`
- `docs/workspace-manager.md`
- `docs/interactive-review-ui.md`
