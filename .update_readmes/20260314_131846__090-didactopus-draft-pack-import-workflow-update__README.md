# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds a **draft-pack import workflow** on top of the workspace manager.

The goal is to let a user take a newly generated draft pack from the ingestion
pipeline and bring it into a managed review workspace in one step.

## Why this matters

A major source of friction in turning online course contents into usable study
domains is not only extraction difficulty, but also the messy handoff between:

- generated draft artifacts
- review workspaces
- ongoing curation
- promoted reviewed packs

That handoff can easily become another activation-energy barrier.

This import workflow reduces that barrier by making it straightforward to:

1. choose a draft pack directory
2. create or target a workspace
3. copy/import the draft pack into that workspace
4. begin review immediately in the UI

## What is included

- workspace import operation
- local API endpoint for importing a draft pack into a workspace
- React UI controls for import
- preservation of imported draft-pack files
- sample import source directory
- sample workspace with imported draft pack

## Core workflow

1. generate a draft pack via ingestion
2. create a workspace or choose an existing one
3. import the draft pack into that workspace
4. open the workspace in the review UI
5. curate and promote it
