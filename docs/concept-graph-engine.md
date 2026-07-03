# Concept Graph Engine

The concept graph engine provides the backbone for Didactopus.

## Features in this revision

- prerequisite reasoning across packs
- cross-pack concept linking
- semantic similarity scoring hook
- curriculum pathfinding
- visualization export
- Epistemap-backed concept epistemic summaries with heuristic and Bayesian
  reliability context

## Edge types

The engine distinguishes between:
- `prerequisite`
- `equivalent_to`
- `related_to`
- `extends`
- `depends_on`

Only prerequisite edges are used for strict learning-order pathfinding.
