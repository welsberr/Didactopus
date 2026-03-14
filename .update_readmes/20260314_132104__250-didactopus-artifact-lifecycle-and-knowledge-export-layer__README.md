# Didactopus Artifact Lifecycle + Knowledge Export Layer

This update extends the worker-backed artifact registry with:

- artifact download support
- retention policy support
- artifact expiration metadata
- lifecycle management endpoints
- learner knowledge export paths

## What it adds

- artifact download API
- retention policy fields on artifacts
- expiry / purge metadata
- artifact state transitions
- knowledge export scaffolding for reuse beyond Didactopus
- guidance for improving packs, producing curriculum outputs, and generating agent skills

## Why this matters

Didactopus should not merely *track* artifacts. It should help manage their lifecycle
and make the knowledge represented by learner activity reusable.

This layer supports two complementary goals:

### 1. Artifact lifecycle management
Artifacts can now be:
- registered
- listed
- downloaded
- marked for retention or expiry
- reviewed for later cleanup

### 2. Knowledge export and reuse
Learner progress can be rendered into structured outputs that may be useful for:
- improving Didactopus domain packs
- drafting traditional curriculum materials
- producing AI-oriented skill packages
- documenting surprising learner discoveries
- supporting mentor review and knowledge capture

## Knowledge export philosophy

A learner should not only consume domain packs; sometimes the learner contributes new
understanding, better examples, clearer misconceptions, or unexpected conceptual links.

Didactopus therefore needs a path from learner activity to reusable artifacts such as:

- concept observations
- misconception notes
- pack-improvement suggestions
- curriculum outlines
- skill manifests
- structured knowledge snapshots

## Strong next step

- true scheduled retention cleanup worker
- signed or permission-checked download tokens
- richer learner-knowledge synthesis pipeline
- export templates for curriculum and skill packages
