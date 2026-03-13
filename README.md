# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform.

This revision upgrades the evidence layer from a single weighted score to a **multi-dimensional mastery model**.

## Added in this revision

- per-concept mastery dimensions:
  - correctness
  - explanation
  - transfer
  - project_execution
  - critique
- weighted, recency-aware dimension summaries
- per-dimension mastery thresholds
- concept-level mastery determined from all required dimensions
- dimension-specific weakness reporting
- adaptive next-step selection informed by weak dimensions
- tests for multi-dimensional mastery promotion and partial weakness detection

## Why this matters

Real mastery is not one scalar.

A learner can be strong at routine correctness and still be weak at transfer, explanation, or critique. This revision lets Didactopus represent that distinction explicitly.
