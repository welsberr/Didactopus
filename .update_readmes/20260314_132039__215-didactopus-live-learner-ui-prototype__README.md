# Didactopus Live Learner UI Prototype

This update connects the learner-facing UI prototype to a live in-browser learner-state
and orchestration loop.

## What this prototype does

It now drives the interface from live state rather than static cards:
- topic/domain selection
- first-session onboarding
- recommendation generation from learner state
- visible mastery-map progress from mastery records
- milestone / reward feedback
- transparent "why this is recommended" explanations
- simulated evidence application that updates learner mastery live
- source attribution / compliance panel for provenance-sensitive packs

## Architecture

### Frontend
A React/Vite single-page prototype that manages:
- learner profile selection
- domain pack selection
- learner mastery records
- recommendation cards
- mastery map rendering
- milestone log
- attribution/compliance display

### State engine
A lightweight JS orchestration layer mirrors the Didactopus Python scaffolds:
- evidence application
- score aggregation
- confidence updates
- prerequisite-gated unlocking
- next-step recommendation generation
- reinforcement targeting
- simple claim-readiness estimation

## Why this matters

This is closer to a human-usable experience:
- the learner can see the effect of actions immediately
- the "why next?" logic is inspectable
- progress feels visible and rewarding
- the system remains simple enough for a novice to approach

## Next likely step

Wire this prototype to a real backend so that:
- domain packs are loaded from pack files
- learner state persists across sessions
- evaluator results update mastery records automatically
- attribution/compliance artifacts are derived from actual ingested sources
