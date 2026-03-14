# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds a **curriculum path quality layer**.

The goal is to analyze whether a pack's roadmap looks like a sensible learner
progression rather than merely a list of stages.

## What is included

- curriculum path quality analysis module
- heuristic checks for stage progression quality
- path-quality findings included in import preview
- UI display for curriculum path warnings
- sample packs and tests

## Current path-quality checks

This scaffold includes checks for:
- empty stages
- stages with no checkpoint activity
- concepts never referenced in checkpoints or projects
- capstones/projects placed very early
- dead-end late stages with no assessment density
- suspicious stage-size imbalance
- abrupt prerequisite-load jumps across stages
