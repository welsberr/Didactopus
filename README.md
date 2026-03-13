# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform.

This revision moves the system from simple concept merging toward a true **merged learning graph**.

## Added in this revision

- merged learning graph builder
- combined prerequisite DAG across packs
- merged roadmap stage catalog
- merged project catalog
- namespaced concept keys (`pack::concept`)
- optional concept override support in `pack.yaml`
- learner-facing roadmap generation from merged packs
- CLI reporting for merged graph statistics
- tests for merged learning graph behavior

## Why this matters

Didactopus can now use multiple compatible packs to build one composite domain model rather than treating packs as isolated fragments.

That enables:
- foundations + extension pack composition
- unified learner roadmaps
- shared project catalogs
- safe coexistence of overlapping concept IDs via namespacing
