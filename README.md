# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform for building genuine expertise through concept graphs, adaptive curriculum planning, evidence-driven mastery, Socratic mentoring, and project-based learning.

**Tagline:** *Many arms, one goal — mastery.*

## Complete overview to this point

Didactopus is designed to support both **human learners** and, potentially, **agentic AI students** that use the same mastery infrastructure to become competent in a target domain.

The current architecture includes:

- **Domain packs** for contributed concepts, projects, rubrics, and mastery profiles
- **Dependency resolution** across packs
- **Merged learning graph** generation
- **Adaptive learner engine** that identifies ready, blocked, and mastered concepts
- **Evidence engine** with weighted, recency-aware, multi-dimensional mastery inference
- **Concept-specific mastery profiles** with template inheritance
- **Concept graph engine** for cross-pack prerequisite reasoning, concept linking, pathfinding, and graph export

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
