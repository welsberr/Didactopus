
# Didactopus

Didactopus is an experimental learning infrastructure designed to support **human learners, AI learners, and hybrid learning ecosystems**. It focuses on representing knowledge structures, learner progress, and the evolution of understanding in ways that are inspectable, reproducible, and reusable.

The system treats learning as an **observable graph process** rather than a sequence of isolated exercises. Concept nodes, prerequisite edges, and learner evidence events together produce a dynamic knowledge trajectory.

Didactopus aims to support:

- individual mastery learning
- curriculum authoring
- discovery of new conceptual connections
- AI‑assisted autodidactic learning
- generation of reusable educational artifacts

---

# Core Concepts

## Domain Packs

A **domain pack** represents a structured set of concepts and relationships.  
Concepts form nodes in a graph and may include:

- prerequisites
- cross‑pack links
- exercises or learning activities
- conceptual metadata

Domain packs can be:

- private (learner owned)
- community shared
- curated / mentor‑reviewed

---

## Learner State

Each learner accumulates **evidence events** that update mastery estimates for concepts.

Evidence events can include:

- exercises
- reviews
- projects
- observations
- mentor evaluation

Mastery records track:

- score
- confidence
- evidence count
- update history

The system stores full evidence history so that learning trajectories can be reconstructed.

---

## Artifact System

Didactopus produces **artifacts** that document learner knowledge and learning trajectories.

Artifacts may include:

- animation bundles
- graph visualizations
- knowledge exports
- curriculum drafts
- derived skill descriptions

Artifacts are tracked using an **artifact registry** with lifecycle metadata.

Artifact lifecycle states include:

- created
- retained
- expired
- deleted

Retention policies allow systems to manage storage while preserving important learner discoveries.

---

# Worker Rendering System

Rendering jobs transform learner knowledge into visual or structured outputs.

Typical workflow:

1. Learner state + pack graph → animation frames
2. Frames exported as SVG
3. Render bundle created
4. Optional FFmpeg render to GIF/MP4

Outputs are registered as artifacts so they can be downloaded or reused.

---

# Knowledge Export

Didactopus supports exporting structured learner knowledge for reuse.

Export targets include:

- improved domain packs
- curriculum material
- AI training data
- agent skill definitions
- research on learning processes

Exports are **candidate knowledge**, not automatically validated truth.  
Human mentors or automated validation pipelines can review them before promotion.

---

# Philosophy: Synthesis and Discovery

Didactopus places strong emphasis on **synthesis**.

Many important discoveries occur not within a single domain, but at the **intersection of domains**.

Examples include:

- mathematics applied to biology
- information theory applied to neuroscience
- physics concepts applied to ecological models

Domain packs therefore support:

- cross‑pack links
- relationship annotations
- visualization of conceptual overlap

These connections help learners discover:

- analogies
- transferable skills
- deeper structural patterns across knowledge fields

The goal is not merely to learn isolated facts, but to build a **network of understanding**.

---

# Learners as Discoverers

Learners sometimes discover insights that mentors did not anticipate.

Didactopus is designed so that learner output can contribute back into the system through:

- knowledge export
- artifact review workflows
- pack improvement suggestions

This creates a **feedback loop** where learning activity improves the curriculum itself.

---

# Intended Uses

Didactopus supports several categories of use:

Human learning
- self‑directed study
- classroom support
- mastery‑based curricula

Research
- studying learning trajectories
- analyzing conceptual difficulty

AI systems
- training agent skill graphs
- evaluating reasoning development

Educational publishing
- curriculum drafts
- visualization tools
- learning progress reports

