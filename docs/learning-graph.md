# Merged Learning Graph

The merged learning graph is the pack-composition layer that connects validated domain packs into one learner-facing prerequisite model.

## What the code builds today

`didactopus.learning_graph.build_merged_learning_graph(...)` produces a `MergedLearningGraph` containing:

- `concept_data`
- `stage_catalog`
- `project_catalog`
- `load_order`
- `graph`

Concept keys are namespaced as:

```text
pack-name::concept-id
```

## Inputs

The merged graph is built from validated `PackValidationResult` objects, typically discovered through `didactopus.artifact_registry.discover_domain_packs(...)`.

## Overrides

Pack manifests can explicitly replace a previously defined concept through:

```yaml
overrides:
  - foundations-statistics::descriptive-statistics
```

If the overriding pack defines `descriptive-statistics`, the merged graph will store that concept under the overridden namespaced key.

## Current exported behaviors

The learning-graph and graph-builder layers currently support:

- merged prerequisite DAG construction
- namespaced prerequisite edges
- stage catalog aggregation
- project catalog aggregation
- concept-graph export through `didactopus.graph_builder`
- learner roadmap generation through `generate_learner_roadmap(...)`

## Relationship to the concept graph

`didactopus.graph_builder.build_concept_graph(...)` takes the merged graph inputs and produces the learner-facing `ConceptGraph`, which powers:

- curriculum path extraction
- ready concept detection
- semantic-link suggestions
- planner scoring

## Known limitations

- stage dependencies are still implicit rather than separately modeled
- cross-pack links are supported but still lightweight
- roadmap generation is pack-derived rather than learner-personalized
- richer graph export/visualization is still evolving
