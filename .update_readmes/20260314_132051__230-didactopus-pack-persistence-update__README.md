# Didactopus Pack + Persistence Prototype

This update connects the learner-facing prototype to:

- **real pack-shaped data files**
- **pack compliance / attribution manifests**
- **persistent learner state** via browser local storage
- a small **Python pack export utility** that converts a Didactopus-style pack directory
  into a frontend-consumable JSON bundle

## What is included

### Frontend
- topic/domain selection from real pack files
- first-session onboarding from pack metadata
- recommendation cards driven by live learner state
- mastery-map progress from pack concepts and persisted learner records
- milestone/reward feedback
- transparent "why this is recommended" explanations
- compliance/provenance display from pack manifest
- persistent learner state across reloads via local storage

### Backend-adjacent tooling
- `pack_to_frontend.py` converts:
  - `pack.yaml`
  - `concepts.yaml`
  - `pack_compliance_manifest.json`
  into a bundle suitable for the learner UI

## Why this matters

This gets Didactopus closer to a usable human-facing system:
- the UI is no longer a static mock
- packs are loadable artifacts
- learner progress persists between sessions
- provenance/compliance data can be shown from real manifests

## Next likely step

Add a real API layer so that:
- learner state is persisted outside the browser
- evaluator runs produce evidence automatically
- multiple users can work against the same pack registry
