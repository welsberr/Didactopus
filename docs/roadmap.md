# Roadmap

Last audited against repository implementation: 2026-08-27.

Status labels distinguish code presence from operational readiness:

- `foundation implemented`: reusable code and tests exist, but the capability is
  not yet a complete learner or steward workflow;
- `prototype implemented`: an end-to-end bounded workflow exists, but broader
  validation or product integration remains;
- `in progress`: this remains an active delivery priority;
- `planned`: no adequate end-to-end implementation exists yet.

Confidence schema and integration changes are coordinated by Epistemap's
`docs/confidence-overhaul-roadmap.md`. Didactopus must keep graph evidential
support, learner response probability, mastery score, and evidence coverage as
separate measures during that migration.

The audited cross-repository status is maintained in Epistemap at
`docs/confidence-overhaul-implementation-status.md`. Didactopus phases D1-D4
are complete for the current confidence-overhaul scope, including the
production-code inventory, ORM/API migrations, typed candidate migration,
calibration integration, installed-package matrix, and compatibility release.

Didactopus consumes the portable confidence contract from Epistemap
`v0.1.0a4`. This immutable Git-tag dependency replaces the implementation SHA.
The Epistemap release adds indexed graph operations and the read-only MCP
transport while preserving the confidence contract.

CiteGeist bibliography graph integration is coordinated by CiteGeist's
`docs/epistemap-knowledge-graph-roadmap.md`. Didactopus consumes reviewed
source trails and bibliographic observations; it must not convert citations,
graph centrality, match scores, or unreviewed candidate-support edges into
source truth or learner mastery.

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
- pass concept-level Epistemap Bayesian reliability summaries into mentor and
  evaluator context when available, without presenting them as final truth
  labels
- keep multi-step sequence runs resumable and extend them with persisted
  learner evidence

Current progress:

- Notebook-backed mentorship can run consecutive reviewed sequence steps,
  preserve each completed session, emit a compact progress ledger, and expose
  the next resumable step index.
- Multi-step runs can persist atomically to an explicit local path, validate
  sequence identity on resume, and append provenance-bearing learner attempts.
  Human attempts remain draft evidence and AI-learner attempts remain
  benchmark-only; neither silently changes mastery.
- Graph-grounded sessions now receive compact Epistemap heuristic and Bayesian
  reliability context, including interval width, effective sample size, and
  prior sensitivity. Mentor and evaluator prompts treat it as calibration
  context rather than a truth or mastery label.
- Source fragments preserve stable fragment IDs and source references. Sessions
  emit draft citation-support practice that distinguishes finding an anchor
  from reviewing whether the source actually supports a claim.

Current code anchors:

- `didactopus.learner_session`
- `didactopus.learner_session_demo`
- `didactopus.graph_retrieval`
- `didactopus.ocw_rolemesh_transcript_demo`

### 1a. Pedagogical learning-path contract and student communication

Status: implemented foundation; learner-pilot validation remains planned

Why this belongs beside the mentor loop:

- A graph-grounded answer is not yet a learning experience. Students need to
  know why an activity matters, what to notice, what to do, and how progress
  will be recognized.
- Didactopus should describe the instructional promise and learning activity;
  CourseKestrel should remain responsible for the student's private workspace,
  local policy decisions, provenance, and integrity review.
- The package should support adaptation from learner feedback without turning
  learner responses into permanent ability, personality, demographic, or
  learning-style labels.

This track is informed by Peter Filene's *The Joy of Teaching* and by the
existing pedagogical research notes in `docs/pedagogical-research-alignment.md`.
Filene's technology examples are historical; the relevant design principles
are dialogue, explicit outcomes, diagnostic listening, active practice,
formative feedback, and sustainable teacher-student boundaries.

Target contract fields and behaviors:

- `promise`: why the path matters and what the learner should be able to do;
- `outcomes`: observable learner actions with stable IDs;
- `means`: readings, explanations, practice, discussion, and transfer tasks;
- `evidence`: artifacts or responses that can demonstrate progress;
- `invitation`: plain-language context for each reading or activity;
- `reading_questions` and `discussion_questions`;
- `activity_type`: recitation, conversation, seminar, case, project, reflection,
  or another declared form;
- `cognitive_level` and prerequisites, using a modest knowing → understanding →
  application/analysis → independent production progression;
- `feedback_mode`, time estimate, accessibility options, and policy scopes;
- explicit participation, privacy, escalation, and communication expectations.

Implemented in `didactopus.pedagogy`:

1. Versioned backward-compatible contract validation with deterministic stable
   IDs, readable activity rendering, and old-package omission defaults.
2. Deterministic path mapping with provenance, prerequisite/workload review
   prompts, and private ungraded diagnostic/reflection records with redacted
   exports.
3. Offline activity templates with simulation debrief, consent, privacy,
   accessibility, participation, and public-release metadata.
4. Bounded attributable formative feedback, humane communication boundaries,
   author alignment review, and an optional-AI audit with deterministic fallback.

Remaining planned validation:

1. Validate the contract with learner pilots using pre/post understanding,
   transfer, calibration, accessibility, workload, and communication measures.
2. Integrate the contract into the full learner-session UI and pack distribution
   workflows.
3. Define a backward-compatible, versioned learning-promise and activity
   contract, with fixtures for packages that omit the new fields.
2. Add private, ungraded entry diagnostics and exit reflections for prior
   knowledge, expectations, confidence, misconceptions, and remaining
   questions.
3. Add structured activity templates for guided observation, retrieval practice,
   compare-and-contrast, cases, debates, role-play, interviews, projects, and
   public-facing artifacts where privacy and consent allow them.
4. Make the mentor loop render “why this matters / what to notice / what to do
   next” and distinguish recitation, conversation, and seminar behavior.
5. Add bounded feedback protocols that identify strengths, one or two important
   problems, why they matter, and a next step without rewriting learner work.
6. Preserve learner agency through choice within bounded alternatives and avoid
   engagement-maximizing pressure, simulated friendship, or emotional diagnosis.
7. Add path-author review for alignment among promise, outcomes, activities,
   evidence, workload, accessibility, and policy.
8. Validate the contract with learner pilots using pre/post understanding,
   transfer, calibration, accessibility, workload, and communication measures.

Interoperability boundary:

- Didactopus publishes provider-authored learning structure, activity intent,
  source references, and declared capability constraints.
- CourseKestrel imports that structure into study tasks and policy scopes,
  retaining private diagnostics, notes, drafts, transcripts, and review history
  locally.
- Evidence exchange returns stable IDs, status, provenance references, and
  review metadata by default, not private learner text.
- Didactopus may consume explicit progress or evidence references, but it must
  not infer mastery from unreviewed AI output, graph centrality, or detector
  scores.

Stage 9 release evidence: the complete local suite passes (308 tests), Python
sources compile, and an offline wheel builds with `pip wheel --no-deps
--no-build-isolation`. The pedagogy APIs do not invoke providers or network
routes. Learner-pilot validation, full learner-session UI integration, live
API/webhook routes, and institutional-policy retrieval remain deferred.

### 2. Local-model adequacy benchmark for constrained hardware

Status: prototype implemented; constrained-hardware validation planned

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
- Epistemap G summaries and Markdown reports for each benchmark run
- groundedness reports comparing pre- and post-mentorship behavior
- comparison reports that relate local-model adequacy to the reliability
  profile of the source graph region used in the task
- recommended deployment profiles for low-end, laptop, and stronger local systems

Current anchors:

- `docs/ai-learner-mentorship-benchmark.md`
- `docs/pedagogical-research-alignment.md`
- `didactopus.ai_learner_benchmark`
- `didactopus.source_spine_transfer_experiment`

Assessment experiments:

- compare mentor responses with no reliability summary, heuristic reliability
  only, Bayesian posterior summary, and both together
- test whether communicating uncertainty improves learner calibration without
  reducing useful practice progress
- track whether prior-sensitive or thin-evidence graph regions require different
  mentor language than stable-support regions

### 3. Access-constrained offline learner appliance

Status: foundation implemented; appliance packaging planned

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

MCP adapter work:

- Add an optional Model Context Protocol (MCP) client/server boundary for local
  learner appliances that can call GroundRecall, CiteGeist, Epistemap, and
  ClaimWright tools while preserving Didactopus learner-facing authority.
- Expose Didactopus tools for pack inspection, learner-session setup,
  notebook-page generation, benchmark-run setup, and progress-ledger export.
- Keep learner records local-only by default; MCP tools must not expose learner
  responses, progress ledgers, or private notes to external services unless the
  steward explicitly enables that route.
- Treat GroundRecall context, CiteGeist source trails, Epistemap reliability
  reports, and ClaimWright findings as imported review/context artifacts, not
  learner mastery scores or automatic instructional decisions.
- Add smoke tests showing that MCP-mediated local operation works without
  network access and that remote/model routes are labeled when enabled.

### 4. Pack capsules and low-bandwidth distribution

Status: manifest and validator implemented; distribution workflow planned

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

Status: text and HTML baseline implemented; learner validation planned

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

Status: prototype implemented; product integration planned

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
- backend diagnostics for concept posterior stability, effective sample size,
  and prior sensitivity before deciding what should be visible to learners

### 9. Adaptive diagnostics and practice refinement

Status: foundation implemented; learner integration planned

Why this matters:

- Learners need clearer answers to “what am I weak at?” and “what should I do next?”
- The repository already has evidence and evaluator machinery that can be surfaced in learner terms.

Target features:

- weak-dimension summaries by concept
- misconception tracking
- remedial branch suggestions
- hint ladders and difficulty control
- oral, short-answer, and compare-and-contrast practice modes
- reliability-aware practice selection that treats fragile, contested, or
  prior-sensitive concepts differently from stable-support concepts

Assessment experiments:

- compare next-step recommendations based only on learner mastery versus
  recommendations that also account for graph posterior stability
- test whether contested-evidence practice improves recognition of unsupported
  assertions and manufactured-doubt patterns
- export learner/model responses as Epistemap G rows to evaluate whether
  reliability-aware practice improves calibration and transfer

### 10. Source-grounded citation transparency

Status: foundation implemented; learner transparency planned

Why it matters:

- Trust depends on showing what is grounded in source material and what is model inference.
- This is especially important for learners using local models with variable quality.

Target features:

- lesson and source-fragment references in explanations
- explicit distinction between cited source support and model inference
- easier inspection of concept-to-source provenance
- optional review-facing reliability panel showing posterior support,
  credible interval width, effective sample size, and prior sensitivity

### 11. Pack quality, review, and concept-graph curation improvements

Status: foundation implemented; curation improvements planned

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

Status: experimental harness implemented; field validation planned

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
2. Define the pedagogical learning-path and activity contract.
3. Add private diagnostics, student-facing invitations, and bounded formative
   feedback to the standard session backend.
4. Build a small model-benchmark harness around that backend.
5. Prototype the offline learner appliance profile with local-only defaults.
6. Define pack capsules and low-bandwidth import/export workflows.
7. Add steward health checks and maintenance commands.
8. Build the standards registry and first Common Cartridge/QTI/xAPI mapping
   crosswalks.
9. Add accessible learner HTML and text-first outputs.
10. Add local TTS and STT support to the same session flow.
11. Expand adaptive practice and diagnostics.
12. Improve review, impact analysis, and incremental update support.
