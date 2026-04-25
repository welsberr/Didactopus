# Roadmap

This document summarizes the current prioritized improvement roadmap for Didactopus as a learner-facing system.

The ordering is intentional. The project should first strengthen the graph-grounded mentor loop that defines the real learner task, then use that stable backbone for local-model evaluation, accessibility work, and broader UX improvements.

## Priorities

### 1. Graph-grounded conversational mentor loop

Status: in progress

Why first:

- It defines the actual learner-facing interaction Didactopus is trying to support.
- It makes later benchmarking and accessibility work target a real session model rather than an abstract idea.
- It uses the graph and source-corpus artifacts already present in the repository.

Near-term scope:

- continue strengthening the learner session backend
- make mentor, practice, and evaluator turns consistently source-grounded
- improve trust-preserving feedback behavior
- extend the session flow beyond one short interaction
- make scientific virtues operational in the session loop by separating observation from interpretation, preserving uncertainty, and rewarding justified revision
- replace stubbed provider output in learner-facing pilot flows with configured real model backends where available

Current code anchors:

- `didactopus.learner_session`
- `didactopus.learner_session_demo`
- `didactopus.graph_retrieval`
- `didactopus.ocw_rolemesh_transcript_demo`

### 2. Local-model adequacy benchmark for constrained hardware

Status: planned

Why next:

- The learner loop should be benchmarked as soon as its task shape is stable.
- Adequate local models on low-cost hardware would materially improve access in underserved regions.
- Didactopus does not need a single perfect model; it needs role-adequate behavior.

Primary questions:

- Which models are adequate for `mentor`, `practice`, and `evaluator` roles?
- What latency, memory, and throughput are acceptable on Raspberry Pi-class hardware?
- Which roles can degrade gracefully to smaller models?

Expected outputs:

- benchmark tasks grounded in the MIT OCW pack
- per-role adequacy scores
- recommended deployment profiles for low-end, laptop, and stronger local systems

### 3. Accessibility-first learner interaction

Status: planned

Why high priority:

- Didactopus has clear potential for learners who do not have access to enough teachers or tutors.
- Blind learners and other accessibility-focused use cases benefit directly from structured, guided interaction.
- Voice and text accessibility can build on the same learner-session backend.

Target features:

- screen-reader-friendly learner output
- accessible HTML alternatives to purely visual artifacts
- text-first navigation of concept neighborhoods and progress
- explicit structural cues in explanations and feedback

### 4. Voice interaction with local STT and TTS

Status: planned

Why after accessibility baseline:

- The project should first ensure that the session structure is accessible in text.
- Voice interaction is more useful once the mentor loop and pending-response behavior are stable.

Target features:

- speech-to-text input for learner answers
- text-to-speech output for mentor, practice, and evaluator turns
- spoken waiting notices during slow local-model responses
- repeat, interrupt, and slow-down controls

### 5. Learner workbench UI

Status: pilot in progress

Why important:

- The repository has review-focused interfaces and generated artifacts, but the learner path is still fragmented.
- A dedicated learner workbench would make Didactopus more usable as a personal mentor rather than only a pipeline/demo system.

Target features:

- current concept and why-it-matters view
- prerequisite chain and supporting lessons
- grounded source excerpts
- active practice task
- evaluator feedback
- recommended next step
- first external pilot should use the `evidence-trail` evo-edu pack as a learner-workbench test case

Current progress:

- the first external pilot pack now exists at `domain-packs/evidence-trail/`
- `pack_to_frontend` output is generated and copied into `webui/public/packs/evidence-trail-pack.json`
- the web UI now has a learner-workbench launcher and `Evidence Trail` pilot mode in addition to the review workbench
- the learner pilot exposes question, observation, interpretation, uncertainty, and revision-trigger fields directly in the UI
- scientific virtues are now reflected in the UI framing and in backend learner-session prompt construction
- the backend now exposes `POST /api/learner-workbench/session`
- end-to-end verification succeeded locally: the API starts, the endpoint returns structured concept/session output, and the frontend/backend contract is working

Immediate next steps:

- replace current stubbed mentor/practice/evaluator text with a configured real provider path
- enrich the `Evidence Trail` pack with grounded source fragments so returned guidance is based on more than pack metadata
- persist learner-session state instead of treating each call as a stateless step
- connect learner progress, evidence, and revision history to the standard backend session model
- define deployment notes for running the learner workbench against the local API outside development mode

Current pilot state:

- a backend learner-workbench path exists in `didactopus.learner_workbench`
- the API exposes `POST /api/learner-workbench/session`
- the web UI now has a launcher that separates review workbench from learner workbench
- the first pilot pack exists at `domain-packs/evidence-trail/`
- the frontend can load a static learner-pack payload from `webui/public/packs/evidence-trail-pack.json`
- the current pilot explicitly emphasizes question framing, observation versus interpretation, uncertainty, and revision

Next steps:

- connect the learner-workbench pilot more directly to the standard learner-session backend
- persist learner-workbench state instead of treating each step as a stateless interaction
- ground the pilot more deeply in source fragments instead of mostly pack-level structure
- decide which scientific-virtues framing belongs in the stable learner path versus remaining pilot-specific
- document a simple local run path for using the learner workbench outside ad hoc development

### 6. Adaptive diagnostics and practice refinement

Status: planned

Why this matters:

- Learners need clearer answers to “what am I weak at?” and “what should I do next?”
- The repository already has evidence and evaluator machinery that can be surfaced in learner terms.

Target features:

- weak-dimension summaries by concept
- misconception tracking
- remedial branch suggestions
- hint ladders and difficulty control
- oral, short-answer, and compare-and-contrast practice modes

### 7. Source-grounded citation transparency

Status: planned

Why it matters:

- Trust depends on showing what is grounded in source material and what is model inference.
- This is especially important for learners using local models with variable quality.

Target features:

- lesson and source-fragment references in explanations
- explicit distinction between cited source support and model inference
- easier inspection of concept-to-source provenance

### 8. Pack quality, review, and concept-graph curation improvements

Status: planned

Why later:

- These are important, but they mainly improve the quality of the learning substrate rather than the immediate learner interaction.
- The graph-first path should first prove out the learner experience it supports.

Target features:

- concept merge and split workflows
- alias handling across packs
- impact analysis for concept edits
- stronger review support for noisy or broad concepts
- improved source coverage QA

### 9. Incremental re-ingestion and course updates

Status: planned

Why useful:

- External course repositories are now part of the intended workflow.
- Didactopus should avoid full rebuilds when only part of a source tree changes.

Target features:

- changed-file detection
- stable concept and fragment IDs where possible
- graph and pack diffs
- preservation of learner evidence across source updates

### 10. Richer multimodal and notation support

Status: longer-term

Why longer-term:

- This work is valuable but more specialized and technically demanding than the earlier roadmap items.

Examples:

- spoken math rendering improvements
- diagram descriptions
- accessible handling of image-heavy source materials
- EPUB and other learner-friendly export targets

## Guiding Principles

- Use the graph and source corpus before relying on model prior knowledge.
- Optimize for guided learning, not answer offloading.
- Prefer role-adequate local models over chasing a single best model.
- Keep accessibility and low-cost deployment in scope from the start, not as cleanup work.
- Preserve provenance and license compliance as first-class constraints.
- Advance the current roadmap without assuming abundant compute, fluent English, expert supervision, or mature learners.
- Treat scientific virtues as operational principles: encourage curiosity, honesty about evidence, skepticism toward weak claims, attentiveness to caveats, and revision when the evidence changes.
- Separate observation from interpretation in learner-facing guidance so the system does not blur grounded support with model inference.
- Frame revision as progress rather than as failure, especially in mentor and evaluator feedback.

## Suggested Implementation Sequence

1. Strengthen `didactopus.learner_session` into the standard session backend.
2. Fold the learner-workbench pilot into that backend without losing its stronger study-state framing.
3. Replace stubbed learner-workbench provider output with a configured real model backend.
4. Ground the `evidence-trail` pilot in richer source fragments and persisted learner state.
5. Build a small model-benchmark harness around the unified learner backend.
6. Add accessible learner HTML and text-first outputs.
7. Add local TTS and STT support to the same session flow.
8. Expand adaptive practice and diagnostics.
9. Improve review, impact analysis, and incremental update support.
