# Evidence Engine

## Purpose

The evidence engine updates learner mastery state from observed work rather than from manual declarations alone.

## Evidence types in this revision

- explanation
- problem
- project
- transfer

Each evidence item includes:
- target concept
- evidence type
- score from 0.0 to 1.0
- optional notes

## Current update policy

For each concept:
- maintain a running average evidence score
- mark as mastered when average score meets mastery threshold and at least one evidence item exists
- resurface a mastered concept when the average later drops below the resurfacing threshold

This is intentionally simple and transparent.

## Future work

- weighted evidence types
- recency decay
- uncertainty estimates
- Bayesian mastery models
- multi-rubric scoring per concept
