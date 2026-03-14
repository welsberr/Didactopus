# Didactopus

This package adds two substantial prototype layers:

1. a **course-ingestion compliance layer**
2. a **real learner-facing UI prototype**

## What this update covers

### Course-ingestion compliance
The compliance layer is designed for domain packs created from open courseware and other external instructional sources.

It includes:
- source inventory handling
- attribution and provenance records
- pack-level license flags
- compliance QA checks
- exclusion tracking for third-party content
- redistribution-risk signaling

### Learner-facing UI prototype
The prototype UI is designed to be usable by humans approaching a new topic.

It implements:
- topic/domain selection
- first-session onboarding
- “what should I do next?” cards
- visible mastery-map progress
- milestone/reward feedback
- transparent “why the system recommends this” explanations

## UX stance

Didactopus should help a novice get moving quickly, not present a second subject to learn first.

The first session should:
- make the next action obvious
- give quick feedback
- show visible progress
- feel encouraging rather than bureaucratic

## Prototype scope

This is still a prototype scaffold, but the UI and compliance pieces are concrete enough to:
- test interaction patterns
- validate data shapes
- demonstrate provenance-aware ingestion
- serve as a starting point for a fuller implementation
