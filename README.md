# Didactopus

![Didactopus mascot](artwork/didactopus-mascot.png)

Didactopus is a local-first educational workbench for turning source material into structured learning domains, grounding tutoring and evaluation in those domains, and exporting knowledge products that other AI systems can use as a skill.

The short version is:

- ingest a course, topic outline, or notes
- build a concept graph and learning path
- review and improve that structure
- use it to support guided human learning
- export grounded knowledge products for AI use

## Project Description

Didactopus sits between raw educational material and both human and AI learning activity.

It is not meant to be a "do the assignment for me" system. Its intended role is closer to a structured mentor, pedagogy workbench, and knowledge-grounding layer. The aim is to reduce confusion, improve sequencing, and make learning more visible without encouraging answer offloading.

At a high level, the repository does six things:

1. Ingest source material such as Markdown, text, HTML, PDF-ish text, DOCX-ish text, and PPTX-ish text into normalized course/topic structures.
2. Distill those structures into draft domain packs with concepts, prerequisites, roadmaps, projects, attribution, and review flags.
3. Validate, review, and promote those packs through a workspace-backed review flow.
4. Build learning graphs, learner sessions, evidence summaries, and capability exports.
5. Support grounded LLM-backed mentor, practice, and evaluator behavior.
6. Export reusable knowledge products and skills from grounded learning artifacts.

## Design And Teaching Philosophy

Didactopus is built around a few core ideas:

- learning should stay effortful for the learner
- guidance should be structured, grounded, and inspectable
- source material should matter more than model prior knowledge
- explanations, critique, and next-step advice should preserve learner trust
- local and low-cost deployment matter for access

It should also operate under a scientific-virtues outlook. In practice that
means Didactopus should reinforce habits such as:

- curiosity about the question rather than premature closure
- honesty about what is observed versus what is inferred
- skepticism toward weakly supported claims, including model-generated claims
- attentiveness to source quality, caveats, and uncertainty
- willingness to revise when better evidence changes the picture

In practice, that means Didactopus tries to help with:

- topic structure
- prerequisite visibility
- study sequencing
- grounded explanation
- practice design
- evaluator feedback
- capability and progress artifacts

It explicitly tries not to become a silent answer surrogate.

The project is also being advanced with a future-compatibility constraint: avoid choices that assume abundant compute, fluent English, expert supervision, or only mature learners. That keeps the current roadmap moving while preserving eventual usefulness for more constrained and equity-sensitive educational settings.

## Who It Is For

Didactopus has several real audiences:

- autodidacts who want a structured mentor scaffold for a topic
- students who want help understanding coursework without outsourcing the work
- instructors, tutors, and curriculum designers who want reviewable concept structures
- technically oriented users who want local, grounded LLM support
- libraries, labs, and other shared-resource settings that may want a more advanced local inference stack

The repo currently serves the technically comfortable user best, but the design direction is broader: grounded, accessible educational support that can work for a single learner or in a shared institutional setting.

## Brief Roadmap

Current priorities are:

1. graph-grounded learner sessions
2. local-model adequacy benchmarking
3. multilingual grounded learner support
4. accessibility-first learner outputs
5. arena-based comparison of model, prompt, and language choices

The live detailed roadmap is in:

- `docs/roadmap.md`
- `docs/multilingual-qa.md`

Didactopus can also generate a starter multilingual QA draft from a pack:

```bash
python -m didactopus.multilingual_qa_seed domain-packs/mit-ocw-information-entropy
```

and promote selected seed entries into a curated multilingual QA spec:

```bash
python -m didactopus.multilingual_qa_review --seed domain-packs/mit-ocw-information-entropy/multilingual_qa.seed.yaml --out domain-packs/mit-ocw-information-entropy/multilingual_qa.yaml --language es --required-term-id shannon-entropy
```

## Start Here If You Just Want To Learn

If your main question is "how quickly can this help me learn something?", start here:

```bash
pip install -e .
python -m didactopus.ocw_information_entropy_demo
python -m didactopus.learner_session_demo
python -m didactopus.ocw_progress_viz
python -m didactopus.ocw_skill_agent_demo
```

Then open:

- `examples/ocw-information-entropy-run/learner_progress.html`
- `examples/ocw-information-entropy-session.json`
- `examples/ocw-information-entropy-session.html`
- `examples/ocw-information-entropy-session.txt`
- `examples/ocw-information-entropy-skill-demo/skill_demo.md`
- `skills/ocw-information-entropy-agent/`

That path gives you:

- a generated domain pack
- a graph-grounded learner session
- accessible HTML and text outputs
- a visible mastery path
- a capability export
- a reusable grounded skill

The point is not to replace your effort. The point is to give your effort structure, feedback, and momentum.

## Basic Learner Use Case

The simplest Didactopus pattern for a human learner is:

1. Start from a topic or course source.
2. Generate a draft pack and path quickly.
3. Use the learner session to get explanation, practice, and feedback.
4. Review only the obvious extraction noise.
5. Keep learning with the grounded structure instead of starting every time from a blank prompt.

For the fastest included example, use the MIT OCW Information and Entropy demo. It is the current end-to-end reference flow for:

- course ingestion
- graph construction
- learner session generation
- progress visualization
- skill export

## Learner Workbench Pilot

Didactopus now also includes a learner-workbench pilot in the web UI.

The current split is:

- review workbench for candidate triage, synthesis, and promotion
- learner workbench pilot for guided study and reflective revision

The learner-workbench pilot currently uses the `Evidence Trail` sample pack and
focuses on:

- question framing
- observation versus interpretation
- source comparison
- bibliography growth
- revision under uncertainty

The backend entrypoint for that pilot is `POST /api/learner-workbench/session`.
The frontend pilot pack payload is [evidence-trail-pack.json](/home/netuser/bin/Didactopus/webui/public/packs/evidence-trail-pack.json), and the underlying pack lives in [domain-packs/evidence-trail](/home/netuser/bin/Didactopus/domain-packs/evidence-trail).

This is still a pilot rather than the final learner UX. It is best understood as
the first integrated learner-workbench path inside the main repository, not as a
finished replacement for the existing learner-session demos.

## `doclift` Bundle Ingestion

When your source material starts as legacy office documents, the intended
boundary is:

1. `doclift` normalizes the source tree into a bundle.
2. `Didactopus` turns that bundle into a draft pack and learning path.
3. `GroundRecall` can import the same bundle directly when you need canonical
   knowledge storage instead of a learner pack.

Example:

```bash
doclift convert-dir /path/to/legacy-course /tmp/doclift-bundle --asset-root /path/to/legacy-course
didactopus doclift-bundle /tmp/doclift-bundle /tmp/didactopus-pack --course-title "Example Course"
```

That command writes the normal draft-pack outputs plus a
`doclift_bundle_summary.json` file that records the bundle-to-pack conversion.

If you already have a reviewed concept in `GroundRecall`, Didactopus can now
pull a pack-ready `groundrecall_query_bundle.json` directly from a
GroundRecall store and carry it through the same pack-generation path:

```bash
didactopus doclift-bundle-groundrecall \
  /path/to/groundrecall-store \
  channel-capacity \
  /tmp/doclift-bundle \
  /tmp/didactopus-pack \
  --course-title "Example Course"
```

That flow:

- exports `groundrecall_query_bundle.json` for the chosen concept
- places it under the generated pack as a declared supporting artifact
- makes the resulting pack consumable by the learner workbench with
  GroundRecall review and graph context intact

If you want just the Notebook page artifact without building a full pack, use
the direct export wrapper:

```bash
didactopus notebook-page-groundrecall \
  /path/to/groundrecall-store \
  channel-capacity \
  /tmp/notebook-page-export
```

That command writes both `groundrecall_query_bundle.json` and
`notebook_page.json` into the output directory.

The fuller bridge workflow is documented in:

- `docs/groundrecall-bridge.md`
- `docs/evo-edu-notebook-pipeline.md`

## Didactopus As Pedagogy Support

Didactopus is broader than a learner chat loop.

It is also meant to support the pedagogy around learning:

- building and reviewing concept structures
- checking prerequisite logic
- generating and comparing practice tasks
- evaluating explanations with trust-preserving critique
- exporting evidence and capability artifacts
- supporting multilingual and accessible outputs

Operationally, the scientific-virtues framing means Didactopus should:

- separate observation from interpretation in learner-facing flows
- reward justified revision rather than answer persistence
- surface uncertainty explicitly instead of smoothing it away
- push learners toward source comparison and evidence quality checks
- avoid presenting confident unsupported synthesis as settled knowledge

This is why the repository contains review workspaces, validation flows, knowledge graphs, and capability export machinery rather than only a chat interface.

## Grounded AI Learner And Skill Production

Didactopus can also produce grounded knowledge products that other AI systems can use.

The current repo demonstrates:

- generating a grounded domain pack from MIT OCW-derived material
- running deterministic and LLM-backed learner-style flows over that pack
- exporting capability and artifact summaries
- packaging those artifacts into a reusable skill bundle

The key idea is that the AI skill should come from the reviewed knowledge product, not from an ungrounded prompt alone.

The main demo commands are:

```bash
python -m didactopus.ocw_information_entropy_demo
python -m didactopus.learner_session_demo --language es
python -m didactopus.ocw_skill_agent_demo
python -m didactopus.model_bench
python -m didactopus.arena --arena-spec configs/arena.example.yaml
```

## LLM Setup Paths

If you want live LLM-backed Didactopus behavior without the complexity of RoleMesh, start with one of these:

1. `ollama` for simple local use
2. `openai_compatible` for simple hosted use
3. `rolemesh` only if you need routing and multi-model orchestration

Low-friction starting configs:

- `configs/config.ollama.example.yaml`
- `configs/config.openai-compatible.example.yaml`

Setup docs:

- `docs/model-provider-setup.md`

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
- `pack_compliance_manifest.json` when a source inventory is provided

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

### 5. Local model integration

Didactopus can now target a RoleMesh Gateway-backed local LLM setup through its `ModelProvider` abstraction.

Main modules:

- `didactopus.model_provider`
- `didactopus.role_prompts`
- `didactopus.rolemesh_demo`

What this enables:

- role-based local model routing
- separate mentor/practice/project-advisor/evaluator prompts
- local heterogeneous compute usage through an OpenAI-compatible gateway
- a clean path to keep tutoring assistance structured instead of offloading learner work

### 6. Agentic learner demos and visualization

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

The generated MIT OCW pack also includes:

- `license_attribution.json`
- `pack_compliance_manifest.json`
- `source_inventory.yaml`

### Try the local RoleMesh integration path

Stubbed local-provider demo:

```bash
python -m didactopus.rolemesh_demo --config configs/config.example.yaml
```

RoleMesh-backed example config:

```bash
python -m didactopus.rolemesh_demo --config configs/config.rolemesh.example.yaml
```

MIT OCW learner transcript through the local-LLM path:

```bash
python -m didactopus.ocw_rolemesh_transcript_demo --config configs/config.rolemesh.example.yaml
```

If your local models are slow, Didactopus now prints pending-status lines while each mentor, practice, learner, or evaluator turn is being generated. For a long manual run, capture both the transcript payload and those live status messages:

```bash
python -u -m didactopus.ocw_rolemesh_transcript_demo \
  --config configs/config.rolemesh.example.yaml \
  --out-dir examples/ocw-information-entropy-rolemesh-transcript \
  2>&1 | tee examples/ocw-information-entropy-rolemesh-transcript/manual-run.log
```

That command leaves the final transcript in `rolemesh_transcript.md` and `rolemesh_transcript.json`, while `manual-run.log` preserves the conversational “working on it” notices during the wait.

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

- [docs/roadmap.md](docs/roadmap.md)
- [docs/arena.md](docs/arena.md)
- [docs/learner-accessibility.md](docs/learner-accessibility.md)
- [docs/local-model-benchmark.md](docs/local-model-benchmark.md)
- [docs/model-provider-setup.md](docs/model-provider-setup.md)
- [docs/course-to-pack.md](docs/course-to-pack.md)
- [docs/learning-graph.md](docs/learning-graph.md)
- [docs/agentic-learner-loop.md](docs/agentic-learner-loop.md)
- [docs/mastery-ledger.md](docs/mastery-ledger.md)
- [docs/workspace-manager.md](docs/workspace-manager.md)
- [docs/interactive-review-ui.md](docs/interactive-review-ui.md)
- [docs/mit-ocw-course-guide.md](docs/mit-ocw-course-guide.md)
- [docs/rolemesh-integration.md](docs/rolemesh-integration.md)
- [docs/faq.md](docs/faq.md)

## MIT OCW Demo Notes

The MIT OCW Information and Entropy demo is grounded in the MIT OpenCourseWare course page and selected unit/readings metadata, then converted into a local course source file for reproducible ingestion. The resulting generated pack and learner outputs are intentionally reviewable rather than presented as authoritative course mirrors.
