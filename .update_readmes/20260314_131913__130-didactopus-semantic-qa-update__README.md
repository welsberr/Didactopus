# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds a **domain-pack semantic QA layer**.

The goal is to go beyond file integrity and cross-file coherence, and start asking
whether a generated Didactopus pack looks semantically plausible as a learning domain.

## Why this matters

A pack may pass structural validation and still have higher-level weaknesses such as:

- near-duplicate concepts with different wording
- prerequisites that look suspiciously thin or over-compressed
- missing bridge concepts between stages
- concepts that are probably too broad and should be split
- concepts with names that imply overlap or ambiguity

Those problems can still slow a learner or curator down, which means they still
contribute to the activation-energy hump Didactopus is meant to reduce.

## What is included

- semantic QA analysis module
- heuristic semantic checks
- semantic QA findings included in import preview
- UI panel for semantic QA warnings
- sample packs showing semantic QA output
- tests for semantic QA behavior

## Current semantic QA checks

This scaffold includes heuristic checks for:

- near-duplicate concept titles
- over-broad concept titles
- suspiciously thin prerequisite chains
- missing bridge concepts between roadmap stages
- concepts with very similar descriptions
- singleton advanced stages with no visible bridge support

## Design stance

This is still a heuristic layer, not a final semantic truth engine.

Its purpose is to surface likely curation issues early enough that a reviewer can
correct them before those issues turn into confusion or wasted effort.
