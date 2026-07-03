# Mastery Ledger

The mastery ledger is the structured record of what a learner has demonstrated.

## Core contents

- learner identity
- target domain or goal
- mastered concepts
- concept-level evidence summaries
- weak dimensions
- artifact records
- generated capability profile

## Exports

This scaffold exports:

- JSON capability profile
- Markdown capability report
- artifact manifest JSON

## Why it matters

The mastery ledger provides an explicit representation of readiness.
It supports both human and AI learners.

## Important caveat

The current scaffold is not a formal certification system. It is a structured
capability report driven by the Didactopus evidence and evaluator pipeline.

## AI Learner Records

AI learner runs should have separate ledger identity and evidence namespaces.
They are useful for benchmarking mentorship and groundedness, but they should
not be merged with human learner mastery records.

AI learner ledgers should record:

- model id, quantization, provider, and route;
- benchmark source bundle;
- pretest, posttest, transfer, and retention summaries;
- hallucination and abstention metrics;
- `G` metric summaries and component scores;
- intervention condition;
- prompt and evaluator versions.
