# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds a **graph-aware prerequisite analysis layer**.

The goal is to inspect a pack not just as a set of files or even as a semantically
plausible curriculum draft, but as an actual dependency graph whose structure may
reveal deeper curation problems.

## Why this matters

A pack can be syntactically valid, cross-file coherent, and even semantically plausible,
yet still have a concept graph that is hard to learn from or maintain. Typical examples:

- prerequisite cycles
- isolated concepts with no curricular integration
- bottleneck concepts with too many downstream dependencies
- suspiciously flat domains with almost no dependency structure
- suspiciously deep chains suggesting over-fragmentation

Those graph problems can still raise the activation-energy cost of using a pack,
because they make learning paths harder to trust and revise.

## What is included

- prerequisite graph analysis module
- cycle detection
- isolated concept detection
- bottleneck concept detection
- flatness and chain-depth heuristics
- graph findings included in import preview
- UI panel for graph-analysis warnings
- sample packs and tests
