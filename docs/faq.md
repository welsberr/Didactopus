# FAQ

## Why add course ingestion?

Because many open or user-supplied courses already encode:
- topic sequencing
- learning objectives
- exercises
- project prompts
- terminology

That makes them strong starting material for draft domain packs.

## Why not just embed all course text?

Because Didactopus needs structured artifacts:
- concepts
- prerequisites
- projects
- rubrics
- mastery cues

A flat embedding store is not enough for mastery planning.

## Why avoid PyKE or another heavy rule engine here?

Dependency stability matters. The current rule-policy adapter keeps rules simple,
transparent, and dependency-light.

## Can the rule layer be replaced later?

Yes. The adapter is designed so a future engine can be plugged in behind the same interface.
