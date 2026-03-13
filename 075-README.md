# Didactopus

![Didactopus mascot](artwork/didactopus-mascot.png)

**Didactopus** is a local-first AI-assisted autodidactic mastery platform for building genuine expertise through concept graphs, adaptive curriculum planning, evidence-driven mastery, Socratic mentoring, and project-based learning.

**Tagline:** *Many arms, one goal — mastery.*

## Recent revisions

### Interactive Domain review

This revision upgrades the earlier static review scaffold into an **interactive local SPA review UI**.

The new review layer is meant to help a human curator work through draft packs created
by the ingestion pipeline and promote them into more trusted reviewed packs.

## Why this matters

One of the practical problems with using open online course contents is that the material
is often scattered, inconsistently structured, awkward to reuse, and cognitively expensive
to turn into something actionable.

Even when excellent course material exists, there is often a real **activation energy hump**
between:

- finding useful content
- extracting the structure
- organizing the concepts
- deciding what to trust
- getting a usable learning domain set up

Didactopus is meant to help overcome that hump.

Its ingestion and review pipeline should let a motivated learner or curator get from
"here is a pile of course material" to "here is a usable reviewed domain pack" with
substantially less friction.

## What is included

- interactive React SPA review UI
- JSON-backed review state model
- curation action application
- promoted-pack export
- reviewer notes and trust-status editing
- conflict resolution support
- README and FAQ updates reflecting the activation-energy goal
- sample review data and promoted pack output

## Core workflow

1. ingest course or topic materials into a draft pack
2. open the review UI
3. inspect concepts, conflicts, and review flags
4. edit statuses, notes, titles, descriptions, and prerequisites
5. resolve conflicts
6. export a promoted reviewed pack

## Why the review UI matters for course ingestion

In practice, course ingestion is not only a parsing problem. It is a **startup friction**
problem. A person may know what they want to study, and even know that good material exists,
but still fail to start because turning raw educational material into a coherent mastery
domain is too much work.

Didactopus should reduce that work enough that getting started becomes realistic.



### Review workflow

This revision adds a **review UI / curation workflow scaffold** for generated draft packs.

The purpose is to let a human reviewer inspect draft outputs from the course/topic
ingestion pipeline, make explicit curation decisions, and promote a reviewed draft
into a more trusted domain pack.

#### What is included

- review-state schema
- draft-pack loader
- curation action model
- review decision ledger
- promoted-pack writer
- static HTML review UI scaffold
- JSON data export for the UI
- sample curated review session
- sample promoted pack output

#### Core idea

Draft packs should not move directly into trusted use.
Instead, they should pass through a curation workflow where a reviewer can:

- merge concepts
- split concepts
- edit prerequisites
- mark concepts as trusted / provisional / rejected
- resolve conflict flags
- annotate rationale
- promote a curated pack into a reviewed pack

#### Status

This is a scaffold for a local-first workflow.
The HTML UI is static but wired to a concrete JSON review-state model so it can
later be upgraded into a richer SPA or desktop app without changing the data contracts.

### Course-to-course merger

This revision adds two major capabilities:

- **real document adapter scaffolds** for PDF, DOCX, PPTX, and HTML
- a **cross-course merger** for combining multiple course-derived packs into one stronger domain draft

These additions extend the earlier multi-source ingestion layer from "multiple files for one course"
to "multiple courses or course-like sources for one topic domain."

## What is included

- adapter registry for:
  - PDF
  - DOCX
  - PPTX
  - HTML
  - Markdown
  - text
- normalized document extraction interface
- course bundle ingestion across multiple source documents
- cross-course terminology and overlap analysis
- merged topic-pack emitter
- cross-course conflict report
- example source files and example merged output

## Design stance

This is still scaffold-level extraction. The purpose is to define stable interfaces and emitted artifacts,
not to claim perfect semantic parsing of every teaching document.

The implementation is designed so stronger parsers can later replace the stub extractors without changing
the surrounding pipeline.


### Multi-Source Course Ingestion

This revision adds a **Multi-Source Course Ingestion Layer**.

The pipeline can now accept multiple source files representing the same course or
topic domain, normalize them into a shared intermediate representation, merge them,
and emit a single draft Didactopus pack plus a conflict report.

#### Supported scaffold source types

Current scaffold adapters:
- Markdown (`.md`)
- Plain text (`.txt`)
- HTML-ish text (`.html`, `.htm`)
- Transcript text (`.transcript.txt`)
- Syllabus text (`.syllabus.txt`)

This revision is intentionally adapter-oriented, so future PDF, slide, and DOCX
adapters can be added behind the same interface.

#### What is included

- multi-source adapter dispatch
- normalized source records
- source merge logic
- cross-source terminology conflict report
- duplicate lesson/title detection
- merged draft pack emission
- merged attribution manifest
- sample multi-source inputs
- sample merged output pack


### Course Ingestion Pipeline

This revision adds a **Course-to-Pack Ingestion Pipeline** plus a **stable rule-policy adapter layer**.

The design goal is to turn open or user-supplied course materials into draft
Didactopus domain packs without introducing a brittle external rule-engine dependency.

#### Why no third-party rule engine here?

To minimize dependency risk, this scaffold uses a small declarative rule-policy
adapter implemented in pure Python and standard-library data structures.

That gives Didactopus:
- portable rules
- inspectable rule definitions
- deterministic behavior
- zero extra runtime dependency for policy evaluation

If a stronger rule engine is needed later, this adapter can remain the stable API surface.

#### What is included

- normalized course schema
- Markdown/HTML-ish text ingestion adapter
- module / lesson / objective extraction
- concept candidate extraction
- prerequisite guess generation
- rule-policy adapter
- draft pack emitter
- review report generation
- sample course input
- sample generated pack outputs


### Mastery Ledger

This revision adds a **Mastery Ledger + Capability Export** layer.

The main purpose is to let Didactopus turn accumulated learner state into
portable, inspectable artifacts that can support downstream deployment,
review, orchestration, or certification-like workflows.

#### What is new

- mastery ledger data model
- capability profile export
- JSON export of mastered concepts and evaluator summaries
- Markdown export of a readable capability report
- artifact manifest for produced deliverables
- demo CLI for generating exports for an AI student or human learner
- FAQ covering how learned mastery is represented and put to work

#### Why this matters

Didactopus can now do more than guide learning. It can also emit a structured
statement of what a learner appears able to do, based on explicit concepts,
evidence, and artifacts.

That makes it easier to use Didactopus as:
- a mastery tracker
- a portfolio generator
- a deployment-readiness aid
- an orchestration input for agent routing

#### Mastery representation

A learner's mastery is represented as structured operational state, including:

- mastered concepts
- evaluator results
- evidence summaries
- weak dimensions
- attempt history
- produced artifacts
- capability export

This is stricter than a normal chat transcript or self-description.

#### Future direction

A later revision should connect the capability export with:
- formal evaluator outputs
- signed evidence ledgers
- domain-specific capability schemas
- deployment policies for agent routing


### Evaluator Pipeline

This revision introduces a **pluggable evaluator pipeline** that converts
learner attempts into structured mastery evidence.

### Agentic Learner Loop

This revision adds an **agentic learner loop** that turns Didactopus into a closed-loop mastery system prototype.

The loop can now:

- choose the next concept via the graph-aware planner
- generate a synthetic learner attempt
- score the attempt into evidence
- update mastery state
- repeat toward a target concept

This is still scaffold-level, but it is the first explicit implementation of the idea that **Didactopus can supervise not only human learners, but also AI student agents**.

## Complete overview to this point

Didactopus currently includes:

- **Domain packs** for concepts, projects, rubrics, mastery profiles, templates, and cross-pack links
- **Dependency resolution** across packs
- **Merged learning graph** generation
- **Concept graph engine** for cross-pack prerequisite reasoning, linking, pathfinding, and export
- **Adaptive learner engine** for ready, blocked, and mastered concepts
- **Evidence engine** with weighted, recency-aware, multi-dimensional mastery inference
- **Concept-specific mastery profiles** with template inheritance
- **Graph-aware planner** for utility-ranked next-step recommendations
- **Agentic learner loop** for iterative goal-directed mastery acquisition

## Agentic AI students

An AI student under Didactopus is modeled as an **agent that accumulates evidence against concept mastery criteria**.

It does not “learn” in the same sense that model weights are retrained inside Didactopus. Instead, its learned mastery is represented as:

- current mastered concept set
- evidence history
- dimension-level competence summaries
- concept-specific weak dimensions
- adaptive plan state
- optional artifacts, explanations, project outputs, and critiques it has produced

In other words, Didactopus represents mastery as a **structured operational state**, not merely a chat transcript.

That state can be put to work by:

- selecting tasks the agent is now qualified to attempt
- routing domain-relevant problems to the agent
- exposing mastered concept profiles to orchestration logic
- using evidence summaries to decide whether the agent should act, defer, or review
- exporting a mastery portfolio for downstream use

## FAQ

See:
- `docs/faq.md`

## Correctness and formal knowledge components

See:
- `docs/correctness-and-knowledge-engine.md`

Short version: yes, there is a strong argument that Didactopus will eventually benefit from a more formal knowledge-engine layer, especially for domains where correctness can be stated in symbolic, logical, computational, or rule-governed terms.

A good future architecture is likely **hybrid**:

- LLM/agentic layer for explanation, synthesis, critique, and exploration
- formal knowledge engine for rule checking, constraint satisfaction, proof support, symbolic validation, and executable correctness checks

## Repository structure


```text
didactopus/
├── README.md
├── artwork/
├── configs/
├── docs/
├── examples/
├── src/didactopus/
├── tests/
└── webui/
```
