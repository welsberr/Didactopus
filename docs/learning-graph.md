# Merged Learning Graph

## Purpose

The merged learning graph is the first learner-facing composite model built from multiple domain packs.

## Features in this revision

- namespaced concept keys: `pack-name::concept-id`
- merged prerequisite DAG
- stage catalog across packs
- project catalog across packs
- optional overrides for previously defined concepts

## Override model

A pack manifest may include:

```yaml
overrides:
  - foundations-statistics::descriptive-statistics
```

If a pack defines concept `descriptive-statistics` and lists the namespaced target above, it may replace that concept in the merged graph.

That is intentionally explicit and conservative.

## Future work

- merged rubric graph
- stage dependency inference
- learner-specific subgraph extraction
- adaptive sequencing from the merged DAG
