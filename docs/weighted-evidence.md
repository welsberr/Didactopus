# Weighted Evidence Model

## Purpose

The earlier evidence engine treated all evidence items equally. This revision adds a more realistic model with:

- evidence-type weights
- recency weighting
- dimension-level rubric storage
- confidence estimates based on weighted support

## Evidence weighting

Default weights:
- explanation: 1.0
- problem: 1.5
- transfer: 2.0
- project: 2.5

## Recency policy

Each evidence item can be marked `is_recent`. Recent items receive a multiplier. This allows weak recent performance to matter more than stale success, which is useful for resurfacing fragile concepts.

## Confidence

Confidence is currently derived from total weighted evidence mass using a saturating function:

`confidence = total_weight / (total_weight + 1.0)`

This is simple, monotonic, and interpretable.

## Current mastery rule

A concept is mastered if:
- weighted mean score >= mastery threshold
- confidence >= confidence threshold

A previously mastered concept resurfaces if:
- weighted mean score < resurfacing threshold
- and recent weak evidence drags its summary downward enough

## Future work

- per-dimension mastery thresholds
- decay by timestamp instead of a boolean recent flag
- Bayesian knowledge tracing
- separate competence vs fluency models
