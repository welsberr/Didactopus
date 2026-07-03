# AI Learner Mentorship Benchmark

Didactopus can use local LLMs as stand-ins for learners when the goal is to
exercise real mentoring behavior against actual source content. This should go
beyond synthetic learner attempts. The learner model should have to demonstrate
what it knows, what it fabricates, what it can learn from source-grounded
mentoring, and what it can transfer after the mentoring interaction.

## Purpose

The benchmark has two linked purposes:

- improve Didactopus practice, mentorship, evaluator, and evidence flows;
- support research on groundedness changes in AI learners, including the
  practical `G` metric from the biological-learning-laws and machine-learning
  research effort.

## Model Roles

Use separate model roles where possible:

- `learner`: usually a smaller or less capable local model;
- `mentor`: a stronger or more reliable model with source access;
- `practice`: a model that can generate prompts from reviewed records;
- `evaluator`: preferably a stronger model plus deterministic checks;
- `reviewer`: human or high-trust review process for benchmark definitions.

The learner model should be isolated from answer keys and evaluator rubrics.
Each run should record model id, quantization, provider, prompt version,
temperature, context length, seed or sampling settings, and route metadata.

## Why Small Models Matter

Smaller local models can be useful learners because they are more likely to be
naive about particular source content, especially obscure fictional works,
newly ingested Library material, local site corpora, or unpublished/private
workbench examples. This naivety is useful only if it is measured.

Do not assume naivety from model size alone. Begin with an initial assessment
that separates:

- correct prior knowledge;
- plausible but unsupported answers;
- explicit uncertainty or abstention;
- source-specific hallucination;
- confabulated citations or quotations;
- overconfident wrong answers.

## Benchmark Loop

The recommended loop is:

1. Select a reviewed source unit, concept, claim family, or fictional work.
2. Build a source-spine assessment set with answer keys and source anchors.
3. Run a source-blind pretest.
4. Score correctness, confidence, abstention quality, hallucination, and source
   specificity.
5. Run a Didactopus mentorship intervention using source-grounded study-aid
   layers, worked examples, faded examples, retrieval practice, and critique
   prompts.
6. Run an immediate posttest with parallel items, not the same prompts.
7. Run transfer probes that require applying the learned structure to new
   examples or distractors.
8. Optionally run a delayed posttest after context reset.
9. Export claim-level rows for the `G` estimator.
10. Record mastery evidence and benchmark artifacts without promoting them as
    human learner evidence.

## Assessment Design

Assessment items should cover:

- direct recall of source facts;
- source-summary accuracy;
- character, concept, or claim identification;
- argument decomposition;
- evidence/source support;
- claim alignment;
- fallacy or misconception recognition;
- transfer to a new but related case;
- abstention when the source does not support an answer.

For fictional works, include details that are unlikely to be robustly present in
generic model pretraining: minor characters, sequence of events, local wording,
motifs, contradictions, and relation changes. Avoid using only famous plot
points from canonical works.

For science or controversy corpora, include distractor claims that are adjacent
but map to different source records or Index to Creationist Claims entries.

## Mentorship Conditions

Useful experimental conditions include:

- `no_intervention`: pretest and posttest without mentoring;
- `source_dump`: source excerpts only;
- `summary_only`: source summary without practice;
- `worked_examples`: source summary plus worked examples;
- `retrieval_practice`: repeated source-grounded retrieval prompts;
- `full_didactopus`: orientation, study-aid layers, worked/faded examples,
  retrieval, evaluator feedback, and next-step planning;
- `causal_timing_calibration`: a full mentoring variant that makes causal
  timing, source support, and confidence calibration explicit;
- `claim_alignment`: full mentoring with explicit candidate-claim
  disambiguation.

These conditions distinguish whether gains come from raw context exposure,
summary, worked examples, retrieval practice, or the full mentoring loop.

## G Metric Export

The practical `G` estimator in the learning-laws project expects rows with:

- `y`: ground-truth correctness label in `{0,1}`;
- `p`: predicted probability or calibrated confidence for `y=1`;
- `env`: environment or slice label.

Didactopus should export claim-level assessment rows:

```csv
run_id,model_id,phase,item_id,claim_id,env,y,p,response_span,source_anchor
```

Recommended environment labels:

- `C`: clean/reference items, close to demonstrated source examples;
- `K`: target or shifted items, including transfer probes, distractors, or
  source-specific details not directly shown during mentoring.

Compute `G_pre`, `G_post`, and a normalized gain:

```text
delta_G = G_post - G_pre
normalized_delta_G = (G_post - G_pre) / max(1 - G_pre, epsilon)
```

The component scores are also important:

- `S_T`: truth-tracking/calibration;
- `S_D`: discrimination between correct and incorrect claims;
- `S_R`: robustness from clean/reference items to target/shifted items.

An AI learner that becomes more fluent but more overconfident may improve a
surface mastery score while worsening `S_T` or hallucination rates. That should
count against the mentoring method.

## Groundedness Metrics

Track these alongside `G`:

- accuracy;
- Brier score;
- expected calibration error when enough samples exist;
- unsupported assertion rate;
- fabricated citation or quotation rate;
- source-anchor precision and recall;
- abstention precision and recall;
- answer-key leakage flags;
- transfer accuracy;
- retention after context reset.

## Artifact Contract

Each benchmark run should emit:

- `ai_learner_bench_run.json`;
- `pretest_responses.jsonl`;
- `mentorship_transcript.jsonl`;
- `posttest_responses.jsonl`;
- `transfer_responses.jsonl`;
- `scored_claims.csv`;
- `g_metric_pre.json`;
- `g_metric_post.json`;
- `groundedness_report.md`.

The run manifest should record source bundle identifiers, access restrictions,
model routes, prompts, randomization, intervention condition, evaluator version,
and whether answer keys were hidden from the learner context.

## Implemented Compact Harness

The initial executable harness is available through:

```bash
PYTHONPATH=src python -m didactopus.ai_learner_benchmark --models gemma4:e4b qwen3:30b --out-dir examples/ai-learner-mentorship/glass-orchard-latest
```

and through the CLI:

```bash
PYTHONPATH=src python -m didactopus.main ai-learner-benchmark --models gemma4:e4b qwen3:30b --out-dir examples/ai-learner-mentorship/glass-orchard-latest
```

The compact harness currently emits:

- `ai_learner_bench_run.json`;
- `scored_claims.csv`;
- `groundedness_report.md`;
- `interactions_<model>.jsonl`;
- `derived_skill_<model>.md`.

The first implemented run used the controlled `The Glass Orchard` microfiction
source with source-blind pretest claims, source-visible posttest/transfer
claims, local Ollama models, JSON-structured mentorship turns, and
JSON-rendered derived study-skill artifacts. The final 2026-06-28 run is under
`examples/ai-learner-mentorship/glass-orchard-20260628-json-artifact/`.
`gemma4:e4b` reached `G_pre=0.333`, `G_post=1.000`, `delta_G=0.667`, and
skill score `1.000`; `qwen3:30b` reached `G_pre=0.333`, `G_post=0.988`,
`delta_G=0.655`, and skill score `0.920`.

## Source-Spine Transfer Harness

The next experiment adds condition comparison and a human pilot packet:

```bash
PYTHONPATH=src python -m didactopus.source_spine_transfer_experiment --models gemma4:e4b qwen3:30b --conditions source_dump summary_only full_didactopus causal_timing_calibration --out-dir examples/ai-learner-mentorship/source-spine-transfer-latest
```

and through the CLI:

```bash
PYTHONPATH=src python -m didactopus.main source-spine-transfer --models gemma4:e4b qwen3:30b --conditions source_dump summary_only full_didactopus causal_timing_calibration --out-dir examples/ai-learner-mentorship/source-spine-transfer-latest
```

This harness uses the controlled argument-rich `The Tidepool Protocol` source.
It compares raw source exposure, source-spine summary, full Didactopus
mentoring, and a causal-timing/calibration variant. AI learners first generate
their own study notes from the assigned condition; posttest and retention-proxy
probes are then source-hidden and notes-only. This makes the benchmark test
whether the condition produced useful, transferable learning notes rather than
whether the model can reread the source.

The harness emits:

- `source_spine_transfer_run.json`;
- `scored_claims.csv`;
- `groundedness_report.md`;
- per-model/per-condition `notes_*.md`, `derived_skill_*.md`, and
  `interactions_*.jsonl`;
- `human_pilot_packet.md`;
- `human_mentor_condition_scripts.md`;
- `human_response_sheet.csv`;
- `human_answer_key.csv`.

The first full local run on 2026-06-28 is under
`examples/ai-learner-mentorship/source-spine-transfer-20260628/`. Across
`gemma4:e4b` and `qwen3:30b`, full Didactopus produced the highest mean
`delta_G_post` (`0.302`) and perfect mean retention-proxy accuracy, while raw
accuracy and `G` diverged in several cases. Notably, Qwen achieved correct
retention answers under full Didactopus while assigning 0.5 confidence, so
accuracy looked perfect but `G` remained at baseline. That is a useful early
signal that `G` is detecting calibration/discrimination information that raw
accuracy misses.

The pedagogical rationale and near-term experiment design rules are summarized
in [pedagogical-research-alignment.md](pedagogical-research-alignment.md).

A focused run of only `causal_timing_calibration` was completed on 2026-06-28
under
`examples/ai-learner-mentorship/source-spine-transfer-causal-timing-20260628-1818/`.
Across `gemma4:e4b` and `qwen3:30b`, the condition reached mean post accuracy
`0.542`, mean retention-proxy accuracy `0.833`, mean `delta_G_post=0.249`,
mean `delta_G_retention=0.333`, and mean skill score `0.750`. `gemma4:e4b`
showed strong calibrated retention (`G_retention=1.000`) but was conservative
on several posttest claims. `qwen3:30b` remained weakly calibrated under this
condition (`G_post=0.352`, `G_retention=0.333`) and answered several supported
claims as unknown. This suggests the condition is diagnostically useful but
needs either better faded practice or source-anchor recall prompts before it can
be treated as a stronger mentoring intervention.

## Local GPU and Model Policy

Local GPU models should be routed through the existing provider boundary,
preferably GenieHive. Before a benchmark, inspect available routes with:

```bash
PYTHONPATH=src python -m didactopus.provider_inspect --config configs/config.geniehive.example.yaml
```

When downloading models for evaluation, record:

- repository or release identifier;
- license;
- parameter count;
- quantization;
- context length;
- download date;
- checksum where available;
- intended role;
- contamination risk notes.

A reasonable evaluation suite should include at least one small learner model,
one medium learner model, and one stronger evaluator/mentor model. The learner
and evaluator should not be the same model for final scoring unless the run is
explicitly marked as self-evaluated.

## Guardrails

AI-learner benchmark outputs are research artifacts, not proof of human
learning effectiveness. They should not be used to claim that a human learner
would benefit without separate validation.

Restricted Library material can be used in private benchmark workbench runs, but
source excerpts, prompts, responses, and reports derived from restricted
material must not be exported to public surfaces.

The evaluator must be allowed to reward "I do not know" when the learner lacks
source support. A mentoring method that suppresses uncertainty and increases
plausible hallucination is a failure even if answer length or fluency improves.
