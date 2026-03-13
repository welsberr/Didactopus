# Dependency Resolution Plan

## Goals

Didactopus should support a pack ecosystem in which contributors can publish reusable foundations and specialized overlays.

Examples:
- a general statistics foundations pack
- a Bayesian statistics extension pack
- an electronics foundations pack
- a marine bioacoustics specialization pack

## Manifest fields

Each `pack.yaml` should include:
- `name`
- `version`
- `didactopus_min_version`
- `didactopus_max_version`
- `dependencies`

Dependencies use a compact form:

```yaml
dependencies:
  - name: statistics-foundations
    min_version: 1.0.0
    max_version: 2.0.0
```

## Validation stages

### Stage 1
- manifest fields exist
- content files exist
- required top-level keys exist

### Stage 2
- internal references are valid
- duplicate IDs are rejected

### Stage 3
- each dependency names an installed pack
- dependency versions satisfy declared ranges
- pack compatibility includes current core version

## Future work

- full semantic version parsing
- cycle detection in dependency graphs
- topological load ordering
- trust and signature policies
