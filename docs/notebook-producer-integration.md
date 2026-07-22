# Notebook Producer Integration

This document defines the generic boundary between a Notebook-style knowledge
producer and Didactopus.

## Responsibilities

The producer owns source selection, normalization, review, rendered concept
pages, export manifests, and publication. It may use doclift, GroundRecall,
CiteGeist, or other tools, but those choices are not part of the Didactopus
contract.

Didactopus owns learner-facing sequencing, scaffold selection, mentorship,
practice, evaluation, and its validation of consumer inputs.

## Minimum exchange

A portable export contains:

- a `didactopus.notebook.learning_sequence.v1` sequence;
- concept scaffold JSON files;
- an optional `didactopus.notebook_scaffold_selection_policy.v1` policy;
- stable concept identifiers and learner-facing URLs;
- provenance fields appropriate to the producer's review process.

The complete repository fixture is
`examples/notebook-learning-sequence/`. It is intentionally domain-neutral so
it can test the contract without a sibling repository or live website.

## Consumption

```bash
didactopus sequence-plan \
  --sequence /path/to/export/learning-paths/course.didactopus.json \
  --notebook-root /path/to/export \
  --selection-policy /path/to/export/learning-paths/course.selection-policy.json
```

The sequence decides order and session handoffs. Concept-local scaffold files
provide questions, answer summaries, evidence checks, misconception guards,
and prompt seeds. The optional policy ranks records without hard-coding domain
rules into Didactopus.

## Publication boundary

Didactopus does not publish the producer's website. Publication remains a
separate, explicitly configured operation with its own allowlist, privacy
checks, credentials, logging, and rollback. See `OPERATIONS.md` for the
repository-owned workflow.
