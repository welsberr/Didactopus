# FAQ

## Why add a full pack validator?

Because import safety is not only about whether files exist. It is also about
whether the pack makes sense as a Didactopus artifact set.

## How does this help with the activation-energy problem?

It reduces uncertainty at a crucial point. Users can see whether a generated pack
is coherent enough to work with before losing momentum in manual debugging.

## What does it validate?

In this scaffold it validates:
- required files
- YAML parsing
- metadata presence
- duplicate concept ids
- roadmap references
- project prerequisite references
- rubric structure
- weak concept entries

## Does validation guarantee quality?

No. It checks structural coherence, not whether the pack is the best possible
representation of a domain.

## Where are validation results shown?

They are included in import preview results and surfaced in the UI.
