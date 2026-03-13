# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform.

This revision upgrades the evidence layer from simple averaging to a more realistic weighted and recency-aware mastery model.

## Added in this revision

- evidence-type weighting
- recency weighting
- confidence estimation from weighted evidence mass
- dimension-level rubric storage
- weighted concept summaries
- mastery decisions using weighted score and confidence
- resurfacing from recent weak evidence
- tests for weighted scoring and recency behavior

## Why this matters

Not all evidence should count equally.

A capstone project or transfer task should usually matter more than a short explanation, and recent poor performance should sometimes matter more than older success. This revision begins to model that explicitly.
