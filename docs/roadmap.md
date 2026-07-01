# Roadmap

This document summarizes the current prioritized improvement roadmap for Didactopus as a learner-facing system.

The ordering is intentional. The project should first strengthen the graph-grounded mentor loop that defines the real learner task, then use that stable backbone for local-model evaluation, accessibility work, and broader UX improvements.

Access-constrained education is now treated as a core design pressure. The
system should be able to serve learners who lack reliable tutors, institutional
support, cloud access, or safe public access to education. That does not mean
Didactopus can promise secrecy or personal safety in hostile environments; it
means offline-first operation, privacy-preserving defaults, low-expertise
stewardship, and reviewed learning packs must shape the roadmap.

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
- implement the mentoring process contract in `docs/mentoring-operational-process.md`
- use study-aid records as layered overlays rather than source replacements
- add claim-alignment and citation-support practice where the domain calls for it
- improve trust-preserving feedback behavior
- extend the session flow beyond one short interaction

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
- Which smaller models are useful as AI learner stand-ins for source-specific
  mentorship experiments?
- What latency, memory, and throughput are acceptable on Raspberry Pi-class hardware?
- Which roles can degrade gracefully to smaller models?
- How much does mentorship improve groundedness, calibration, transfer, and
  hallucination resistance?

Expected outputs:

- benchmark tasks grounded in the MIT OCW pack
- per-role adequacy scores
- source-blind pretest, posttest, transfer, and retention runs for AI learners
- `scored_claims.csv` exports for practical `G` estimation
- groundedness reports comparing pre- and post-mentorship behavior
- recommended deployment profiles for low-end, laptop, and stronger local systems

Current anchors:

- `docs/ai-learner-mentorship-benchmark.md`
- `docs/pedagogical-research-alignment.md`
- `didactopus.ai_learner_benchmark`
- `didactopus.source_spine_transfer_experiment`

### 3. Access-constrained offline learner appliance

Status: planned

Why high priority:

- Learners in under-resourced or hostile settings may not be able to rely on
  human tutors, cloud services, or public institutional support.
- Reducing dependence on technically privileged operators is part of the
  educational mission, not only a packaging concern.
- Offline-first, local-only operation improves privacy and resilience even for
  ordinary personal learning.

Target features:

- repeatable single-machine learner-node profile
- no default telemetry or automatic remote calls
- local-only learner ledger by default
- local search and local model routing
- setup health check and "ready for learning" report
- explicit labeling of remote routes when enabled
- plain-language steward documentation
- local export, archive, and deletion workflows for learner records

Current anchors:

- `docs/access-constrained-mentoring.md`
- `docs/deployment-modes.md`
- `docs/interoperability-and-feature-adoption.md`

### 4. Pack capsules and low-bandwidth distribution

Status: planned

Why this follows the appliance:

- An offline learner appliance is only useful if it can receive reviewed,
  immediately usable learning material.
- Pack distribution must not assume Git, Python, or continuous internet access.

Target features:

- pack capsule manifest with content, license, checksums, language,
  accessibility features, model requirements, and review status
- import from local directory, archive file, or removable media
- signed pack verification when signing infrastructure exists
- printable learner and steward guides generated from pack metadata
- low-bandwidth update bundles and local mirror support
- reviewed coverage ledgers that say what a pack does and does not teach
- boundary adapters for Common Cartridge, QTI, EPUB, ZIM/static web bundles,
  and H5P package metadata where mappings are reliable

### 5. Steward experience and maintenance

Status: planned

Why this matters:

- A deployment model that requires a sophisticated technologist at every site
  will not solve the access problem.
- The practical operator should become a local steward, not necessarily an
  expert system administrator.

Target features:

- installer profiles for single learner, shared device, small LAN, and kiosk
- plain-language diagnostics for model, disk, pack integrity, and offline mode
- backup, restore, export, deletion, update, and repair workflows
- recovery path for corrupted indexes, missing models, and failed imports
- advanced configuration still available for expert maintainers but not
  required for normal operation

### 6. Accessibility-first learner interaction

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

### 7. Voice interaction with local STT and TTS

Status: planned

Why after accessibility baseline:

- The project should first ensure that the session structure is accessible in text.
- Voice interaction is more useful once the mentor loop and pending-response behavior are stable.

Target features:

- speech-to-text input for learner answers
- text-to-speech output for mentor, practice, and evaluator turns
- spoken waiting notices during slow local-model responses
- repeat, interrupt, and slow-down controls

### 8. Learner workbench UI

Status: planned

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

### 9. Adaptive diagnostics and practice refinement

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

### 10. Source-grounded citation transparency

Status: planned

Why it matters:

- Trust depends on showing what is grounded in source material and what is model inference.
- This is especially important for learners using local models with variable quality.

Target features:

- lesson and source-fragment references in explanations
- explicit distinction between cited source support and model inference
- easier inspection of concept-to-source provenance

### 11. Pack quality, review, and concept-graph curation improvements

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

### 12. Incremental re-ingestion and course updates

Status: planned

Why useful:

- External course repositories are now part of the intended workflow.
- Didactopus should avoid full rebuilds when only part of a source tree changes.

Target features:

- changed-file detection
- stable concept and fragment IDs where possible
- graph and pack diffs
- preservation of learner evidence across source updates

### 13. Human pilot and field-readiness evaluation

Status: planned

Why later:

- The mentoring loop, offline appliance, pack capsules, and privacy defaults
  need to be stable before higher-risk or access-constrained pilots.
- Human-rights-sensitive deployments require local social, legal, and personal
  risk assessment beyond normal product testing.

Target features:

- low-risk pilots before any high-risk deployment
- learning evaluation with pretest, posttest, retention, and calibration
- steward-maintenance friction measures
- privacy and data-retention review
- red-team review for unsafe model behavior and accidental remote exposure

### 14. Richer multimodal and notation support

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
- Treat access-constrained education as a core deployment concern.
- Make offline-first and no-telemetry defaults the basic learner-node posture.
- Reduce operator privilege requirements through steward-friendly setup and
  maintenance paths.
- Preserve provenance and license compliance as first-class constraints.
- Do not promise secrecy, anonymity, or legal safety for hostile environments.

## Suggested Implementation Sequence

1. Strengthen `didactopus.learner_session` into the standard session backend.
2. Build a small model-benchmark harness around that backend.
3. Prototype the offline learner appliance profile with local-only defaults.
4. Define pack capsules and low-bandwidth import/export workflows.
5. Add steward health checks and maintenance commands.
6. Build the standards registry and first Common Cartridge/QTI/xAPI mapping
   crosswalks.
7. Add accessible learner HTML and text-first outputs.
8. Add local TTS and STT support to the same session flow.
9. Expand adaptive practice and diagnostics.
10. Improve review, impact analysis, and incremental update support.
