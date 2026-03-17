# Local Model Benchmark

Didactopus should not evaluate local models as generic chatbots. It should evaluate them as role-specific components in a graph-grounded learner workflow.

This benchmark uses the MIT OCW Information and Entropy skill bundle and measures whether a local model is adequate for the current Didactopus mentor loop.

## What It Benchmarks

The current harness evaluates three Didactopus roles:

- `mentor`
- `practice`
- `evaluator`

Each role is prompted with graph-grounded context derived from:

- `knowledge_graph.json`
- `source_corpus.json`
- the generated OCW skill bundle

## Why This Matters

Didactopus needs local models that are good enough to support guided learning on constrained hardware. That is a different question from asking which model is globally strongest.

The benchmark is intended to support comparisons such as:

- Raspberry Pi-class devices
- low-end local desktops
- stronger local workstations
- RoleMesh-routed local model mixes

## How To Run It

Stub or local-demo run:

```bash
python -m didactopus.model_bench \
  --config configs/config.example.yaml \
  --skill-dir skills/ocw-information-entropy-agent \
  --out-dir examples/model-benchmark \
  --hardware-profile pi-minimal \
  --hardware-cpu cortex-a76 \
  --hardware-ram-gb 8
```

RoleMesh-backed run:

```bash
python -m didactopus.model_bench \
  --config configs/config.rolemesh.example.yaml \
  --skill-dir skills/ocw-information-entropy-agent \
  --out-dir examples/model-benchmark-rolemesh \
  --hardware-profile laptop-local \
  --hardware-cpu ryzen-7 \
  --hardware-ram-gb 32
```

## Outputs

The benchmark writes:

- `model_benchmark.json`
- `model_benchmark.md`

These include:

- provider and model information
- hardware profile metadata
- per-role latency
- per-role adequacy score and adequacy rating
- an overall recommendation

## Current Scoring Shape

The current heuristic scoring asks whether each role does the right kind of work:

- `mentor`
  - stays tied to the grounded concept
  - surfaces structure or prerequisites
  - asks a focused learner question
- `practice`
  - produces a real exercise
  - avoids giving away the full solution
  - stays tied to the grounded topic
- `evaluator`
  - acknowledges learner strengths
  - preserves an existing caveat rather than inventing an omission
  - gives a concrete next step

This is deliberately narrower than a general-purpose benchmark. Didactopus cares about trustworthy learner guidance, not maximal generic fluency.

## Interpreting Ratings

- `adequate`
  - suitable for local guided-learning experiments
- `borderline`
  - usable only with review and caution
- `inadequate`
  - not recommended for learner-facing use in the current configuration

## Recommended Next Step

As the learner session backend grows, the benchmark should expand to include:

- multi-turn sessions
- first-token delay and tokens-per-second capture
- memory and thermal observations on constrained hardware
- accessibility-specific checks for structure and spoken-output quality
