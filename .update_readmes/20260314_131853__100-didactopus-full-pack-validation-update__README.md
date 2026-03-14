# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds a **full pack-validation layer** that checks cross-file coherence
for Didactopus draft packs before import and during review.

The goal is to move beyond “does the directory exist and parse?” toward a more
Didactopus-native notion of whether a pack is structurally coherent enough to use.

## Why this matters

A generated pack may look fine at first glance and still contain internal problems:

- roadmap stages referencing missing concepts
- projects depending on nonexistent concepts
- duplicate concept ids
- rubrics with malformed structure
- empty or weak metadata
- inconsistent pack identity information

Those issues can become another activation-energy barrier. A user who has already
done the hard work of finding course materials and generating a draft pack should
not have to manually discover every structural issue one file at a time.

## What is included

- full pack validator
- cross-file validation across:
  - `pack.yaml`
  - `concepts.yaml`
  - `roadmap.yaml`
  - `projects.yaml`
  - `rubrics.yaml`
- validation summary model
- import preview now includes pack-validation findings
- review UI panels for validation errors and warnings
- sample valid and invalid packs
- tests for coherence checks

## Core checks

Current scaffold validates:

- required files exist
- YAML parsing for all key files
- pack metadata presence
- duplicate concept ids
- roadmap concepts exist in `concepts.yaml`
- project prerequisites exist in `concepts.yaml`
- rubric structure presence
- empty or suspiciously weak concept entries

## Design stance

This is a structural coherence layer, not a guarantee of pedagogical quality.
It makes the import path safer and clearer, while still leaving room for later
semantic and domain-specific validation.
