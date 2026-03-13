# Didactopus

![Didactopus mascot](artwork/didactopus-mascot.png)

**Didactopus** is a local-first AI-assisted autodidactic mastery platform for building genuine expertise through concept graphs, adaptive curriculum planning, evidence-driven mastery, Socratic mentoring, and project-based learning.

**Tagline:** *Many arms, one goal — mastery.*

## This revision

This revision adds a **graph-aware planning layer** that connects the concept graph engine to the adaptive and evidence engines.

The new planner selects the next concepts to study using a utility function that considers:

- prerequisite readiness
- distance to learner target concepts
- weakness in competence dimensions
- project availability
- review priority for fragile concepts
- semantic neighborhood around learner goals

## Why this matters

Up to this point, Didactopus could:
- build concept graphs
- identify ready concepts
- infer mastery from evidence

But it still needed a better mechanism for choosing **what to do next**.

The graph-aware planner begins to solve that by ranking candidate concepts according to learner-specific utility instead of using unlocked prerequisites alone.

## Current architecture overview

Didactopus now includes:

- **Domain packs** for concepts, projects, rubrics, mastery profiles, templates, and cross-pack links
- **Dependency resolution** across packs
- **Merged learning graph** generation
- **Concept graph engine** with cross-pack links, similarity hooks, pathfinding, and visualization export
- **Adaptive learner engine** for ready/blocked/mastered concept states
- **Evidence engine** with weighted, recency-aware, multi-dimensional mastery inference
- **Concept-specific mastery profiles** with template inheritance
- **Graph-aware planner** for utility-ranked next-step recommendations

## Planning utility

The current planner computes a score per candidate concept using:

- readiness bonus
- target-distance bonus
- weak-dimension bonus
- fragile-concept review bonus
- project-unlock bonus
- semantic-similarity bonus

These terms are transparent and configurable.

## Agentic AI students

This planner also strengthens the case for **AI student agents** that use Didactopus as a structured mastery environment.

An AI student could:

1. inspect the graph
2. choose the next concept via the planner
3. attempt tasks
4. generate evidence
5. update mastery state
6. repeat until a target expertise profile is reached

This makes Didactopus useful as both:
- a learning platform
- a benchmark harness for agentic expertise growth

## Core philosophy

Didactopus assumes that real expertise is built through:

- explanation
- problem solving
- transfer
- critique
- project execution

The AI layer should function as a **mentor, evaluator, and curriculum partner**, not an answer vending machine.

## Domain packs

Knowledge enters the system through versioned, shareable **domain packs**. Each pack can contribute:

- concepts
- prerequisites
- learning stages
- projects
- rubrics
- mastery profiles
- profile templates
- cross-pack concept links

## Concept graph engine

This revision implements a concept graph engine with:

- prerequisite reasoning across packs
- cross-pack concept linking
- semantic concept similarity hooks
- automatic curriculum pathfinding
- visualization export for mastery graphs

Concepts are namespaced as `pack-name::concept-id`.

### Cross-pack links

Domain packs may declare conceptual links such as:

- `equivalent_to`
- `related_to`
- `extends`
- `depends_on`

These links enable Didactopus to reason across pack boundaries rather than treating each pack as an isolated island.

### Semantic similarity

A semantic similarity layer is included as a hook for:

- token overlap similarity
- future embedding-based similarity
- future ontology and LLM-assisted concept alignment

### Curriculum pathfinding

The concept graph engine supports:

- prerequisite chains
- shortest dependency paths
- next-ready concept discovery
- reachability analysis
- curriculum path generation from a learner’s mastery state to a target concept

### Visualization

Graphs can be exported to:

- Graphviz DOT
- Cytoscape-style JSON

## Evidence-driven mastery

Mastery is inferred from evidence such as:

- explanations
- problem solutions
- transfer tasks
- project artifacts

Evidence is:

- weighted by type
- optionally up-weighted for recency
- summarized by competence dimension
- compared against concept-specific mastery profiles

## Multi-dimensional mastery

Current dimensions include:

- `correctness`
- `explanation`
- `transfer`
- `project_execution`
- `critique`

Different concepts can require different subsets of these dimensions.

## Agentic AI students

Didactopus is also architecturally suitable for **AI learner agents**.

An agentic AI student could:

1. ingest domain packs
2. traverse the concept graph
3. generate explanations and answers
4. attempt practice tasks
5. critique model outputs
6. complete simulated projects
7. accumulate evidence
8. advance only when concept-specific mastery criteria are satisfied

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
