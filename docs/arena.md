# Didactopus Arena

The Didactopus arena compares candidate combinations of:

- provider configuration
- model choice
- role prompt variant
- output language

It is not a generic chatbot arena. It is a Didactopus-specific behavior arena for grounded learner tasks.

## What It Does

For each candidate, the arena runs the current graph-grounded learner-task shape for:

- `mentor`
- `practice`
- `evaluator`

It then produces:

- deterministic role scores
- candidate rankings
- a human review queue
- an optional LLM-written review summary to help the human reviewer triage results

## Why This Exists

Didactopus needs a practical way to improve:

- local model choice
- prompt variants
- trust-preserving behavior
- source-grounded behavior

This is an aid to benchmarking and review, not an automatic certification system.

## How To Run It

Use the example spec:

```bash
python -m didactopus.arena --arena-spec configs/arena.example.yaml
```

That writes outputs under:

- `examples/arena/`

## Spec Shape

The arena spec is a YAML file with:

- `candidates`
- `review`

Example candidate fields:

- `name`
- `config`
- `prompt_variant`
- `language`

Example review fields:

- `enabled`
- `config`
- `role`

## Current Prompt Variants

- `baseline`
- `strict_grounding`
- `trust_preserving`
- `concise`

These are applied to Didactopus role prompts, not to arbitrary raw prompt strings.

## Outputs

The arena currently writes:

- `arena_results.json`
- `arena_review_queue.json`
- `arena_report.md`

## Human Review Position

The LLM review summary should be treated as initial triage support only.

The intended order of trust is:

1. deterministic checks
2. arena comparison results
3. LLM comparative summary
4. human reviewer decision
