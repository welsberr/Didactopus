# Didactopus

Didactopus is a local-first AI-assisted autodidactic mastery platform built around
concept graphs, evaluator-driven evidence, adaptive planning, mastery ledgers,
curriculum ingestion, and human review of generated draft packs.

## This revision

This revision adds an **import validation and safety layer** to the draft-pack
import workflow.

The goal is to make importing generated packs into review workspaces safer,
clearer, and easier to trust.

## Why this matters

If the draft-pack import step is risky or opaque, it becomes another point where
a user may hesitate or stall. That would undercut the broader goal of helping
users get over the activation-energy hump of turning online course contents into
usable Didactopus learning domains.

This layer reduces that risk by adding:

- required-file validation
- schema/version summary inspection
- overwrite warnings
- import preview endpoint
- import error reporting
- basic pack-health reporting before copy/import

## What is included

- draft-pack validator
- import preview model
- overwrite-safety checks
- preview and import API endpoints
- updated React UI for preview-before-import
- sample valid and invalid draft packs
- tests for validation and safety behavior

## Core workflow

1. point the UI at a source draft-pack directory
2. preview validation results
3. review warnings or blocking errors
4. choose whether overwrite is allowed
5. import into workspace
6. continue directly into review
