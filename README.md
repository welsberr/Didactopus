# Didactopus

![Didactopus mascot](artwork/didactopus-mascot.png)

**Didactopus** is a local-first AI-assisted autodidactic mastery platform for building genuine expertise through concept graphs, adaptive curriculum planning, evidence-driven mastery, Socratic mentoring, and project-based learning.

**Tagline:** *Many arms, one goal — mastery.*

## Recent revisions

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
├── domain-packs/
├── src/didactopus/
└── tests/
```


