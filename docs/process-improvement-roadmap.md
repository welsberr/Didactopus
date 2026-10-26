# Didactopus process review and improvement roadmap

Reviewed 3 October 2026. Status: proposed implementation plan; review complete,
fixes not implemented by this change.

## Decision

Make provider selection truthful and structured results reliable before judging
local models as mentors or evaluators. Then use reviewed educational cases to
measure grounding and feedback quality, followed by session-performance work.

Start the reviewed pilot with **Flash Q2 for interactive roles** and **27B Q4
for a one-P40 deployment**. Keep **Flash IQ3 as a comparison candidate** until
it demonstrates a task-specific benefit. A larger or less compressed model is
not evidence of better teaching. Laya may suggest request categories; it is not
qualified to grade responses or determine mastery.

## Scope and evidence

The review covered provider configuration and dispatch, learner-session prompts,
model and AI-learner benchmarks, citation extraction, tests, and existing plans
at commit `6a5eea37ddf288efbffa3cff25e6be452f4a1e3d`. The checkout was clean before
this documentation change. This was a bounded review with offline probes, not
a full audit or a new live-model benchmark. No service, learner record, or
mastery state changed.

Existing strengths include source-grounded role prompts, explicit draft learner
evidence, sequence identity checks and atomic run persistence, citation fragment
anchors, pack review, and CI. Preserve these. The richer AI-learner and transfer
harnesses already exist; the next step is to connect and qualify them, not
invent a second evaluation system.

### Confirmed findings

| ID | Finding and evidence | Consequence |
|---|---|---|
| DD-F1 | Both shipped `config.openai-compatible.example.yaml` and `config.ollama.example.yaml` return `[stubbed-response]` through [ModelProvider](../src/didactopus/model_provider.py). An unknown provider name does too. Reproduced without network calls. | Documented setup can appear to work without invoking a model. |
| DD-F2 | [config.py](../src/didactopus/config.py) defines gateway settings under `geniehive` and `rolemesh`. The active gateway client appends `/v1/chat/completions`, uses `X-Api-Key`, and defaults to 30 seconds. | Hosted-provider examples have a different configuration/authentication contract. URL and auth behavior need explicit tests. |
| DD-F3 | [model_bench.py](../src/didactopus/model_bench.py) gives each of `Entropy prerequisite?`, `Practice entropy.`, and `Good limitation. Next.` a role score of 1.0. Reproduced. | Keyword checks can screen response shape but cannot establish instructional adequacy. |
| DD-F4 | The same benchmark derives the exported `y` label from its own adequacy rating and `p` from the underlying adequacy score. | These rows describe heuristic behavior; they do not supply independent truth labels or calibrated probabilities. |
| DD-F5 | [ai_learner_benchmark.py](../src/didactopus/ai_learner_benchmark.py) has a separate Ollama client, also used by [source_spine_transfer_experiment.py](../src/didactopus/source_spine_transfer_experiment.py). Its answer parser accepted non-finite confidence in an offline probe and supplies defaults for missing confidence. | Transport and validation vary by workflow; repaired/defaulted responses can affect calibration analysis. |
| DD-F6 | The general provider returns text/provider/model name but discards token usage and finish reason. It waits for a complete non-streaming response. [learner_session.py](../src/didactopus/learner_session.py) makes sequential bounded role calls. | End-to-end timing, truncation, queue delay, and failures are hard to diagnose from the returned object. |

### Baseline checks

Using the installed Python environment, from the repository root:

```bash
python -m pytest -q tests/test_config.py tests/test_model_provider.py tests/test_model_bench.py tests/test_learner_session.py tests/test_ai_learner_benchmark.py tests/test_source_spine_transfer_experiment.py
```

Result: **46 passed in 0.56 seconds**, using
`/home/netuser/bin/mambaforge/bin/python`. The provider and malformed-output
probes found cases outside that coverage. This result is not whole-suite or
live-model qualification.

## Delivery sequence

### Additional issue fixes and regression checks

All items below are **open**. They turn the additional review findings into
specific fixes within DD-1–DD-6. Close an item only after its regression check
passes and the implementation and test evidence are linked here.

- [ ] **DD-FIX-1 — silent provider substitution (P0; DD-F1; DD-1).** Make
  provider dispatch exhaustive and permit stub responses only for an explicit
  demo configuration. Parameterize `tests/test_model_provider.py` over the
  shipped Ollama and OpenAI-compatible configurations and an unknown name.
  Supported configurations must reach their intended mocked transport; an
  unsupported configuration must raise a clear configuration error. Keep a
  separate passing test for intentional stub mode.
- [ ] **DD-FIX-2 — provider configuration mismatch (P0; DD-F2; DD-1).**
  Align configuration fields, URL joining, authentication, and timeout settings
  with the selected adapter. Test trailing slashes, the documented base-URL
  convention, bearer versus gateway authentication, and role overrides. Assert
  the exact outbound request and verify inspection output redacts credentials.
- [ ] **DD-FIX-3 — keyword-only qualification (P0 reporting repair, P1
  quality evaluation; DD-F3; DD-3).** Keep keyword scores labeled as heuristics,
  but remove their ability to qualify a model for teaching. Add the exact probes
  `Entropy prerequisite?`, `Practice entropy.`, and `Good limitation. Next.` to
  `tests/test_model_bench.py`; high heuristic scores must still leave pedagogical
  qualification unevaluated without independent reviewed evidence.
- [ ] **DD-FIX-4 — circular evaluation labels (P0; DD-F4; DD-3).** Stop
  presenting a threshold of the heuristic score as independent correctness
  `y`, or the same score as calibrated probability `p`. Retain those values in
  explicitly typed heuristic records. Require independent label provenance and
  a declared probability interpretation for calibration/G evaluation; otherwise
  report the metric unavailable. Test both missing-label rejection and a valid
  independently labeled fixture. Preserve historical exports with versioned
  interpretation rather than silently rewriting them.
- [ ] **DD-FIX-5 — invalid or invented confidence (P0; DD-F5; DD-2).**
  Reject NaN, infinities, booleans, and out-of-range probabilities in strict
  assessment mode. Treat missing confidence as missing, not as a measured 0.5
  or 0.7. Add these cases to `tests/test_ai_learner_benchmark.py`, including
  `{"answer":"true","confidence":NaN}` and `{"answer":"true"}`. Neither
  may enter calibration as a normal scored response. Keep answer accuracy
  separately assessable when the answer itself is valid; report the missing
  calibration observation and its denominator explicitly.
- [ ] **DD-FIX-6 — divergent benchmark clients (P0; DD-F5; DD-2).** Route
  compact and transfer experiments through the shared provider/validation
  contract. Replay the same valid, invalid, timed-out, and repaired responses
  through both harnesses. They must produce consistent statuses while retaining
  raw output and parser versions. Any legacy recovery remains explicit.
- [ ] **DD-FIX-7 — discarded completion metadata (P0 for truncation,
  P1 for timing; DD-F6; DD-2/DD-4).** Retain finish reason, usage when supplied,
  elapsed time, and provider outcome. Inject a length-limited completion:
  incomplete structured output must not enter scored records, and a prose turn
  must expose its incomplete status. Missing usage must remain unknown, not zero.

P0 means required before model qualification or expanded learner-facing use;
P1 means required for a reviewed pilot; P2 means operational refinement after
those gates. Assign an implementation owner at the start of each package.
These are ordered work packages, not new calendar commitments.

### DD-1 — make provider configuration executable and explicit (P0)

Addresses DD-F1–F2. Independent of GroundRecall's integration gate.

- Accept only supported provider names. Make `stub` an explicit demo choice;
  unsupported names or missing live configuration must fail with an actionable
  error. Add an explicit simulation marker to demo receipts.
- Implement the advertised Ollama and OpenAI-compatible adapters, or mark them
  unavailable and correct the setup guide until implementation is ready.
  Preserve existing GenieHive/RoleMesh compatibility through named migrations.
- Define URL joining, model aliases, authentication schemes, timeouts, output
  budgets, structured-output support, streaming, and usage reporting as provider
  capabilities. A server listing models is not proof of a successful inference.
- Extend provider inspection with configuration validation and a separate,
  explicitly requested bounded inference check. Redact credentials from reports.
- Supply a tested llama.cpp profile. The existing gateway dispatch can reach a
  direct unauthenticated local endpoint; do not assume its `X-Api-Key` behavior
  implements bearer authentication for other servers.

**Acceptance:** every shipped configuration has a fixture-backed dispatch test.
Unknown providers cannot silently generate demo output. Mock HTTP tests assert
the exact URL, headers, role mapping, and request body. A bounded live check
records the requested and returned model, a real response, and explicit failure
when unavailable. Stub runs are ineligible for model qualification.

### DD-2 — validate structured outcomes and preserve request evidence (P0)

Addresses DD-F5–F6. Define the contract alongside DD-1, then use it across clients.

- Add a structured response type retaining content, finish reason, model and
  runtime identity where known, token usage when available, elapsed time,
  provider outcome, and validation status. Record unavailable metrics as unknown.
- Use versioned task schemas for assessment answers and generated artifacts.
  Require finite probabilities in the declared range; distinguish absent
  confidence, valid abstention, malformed response, and transport failure.
- Keep strict qualification parsing separate from optional legacy recovery.
  Any repair, default, or scale conversion must be recorded. Do not turn missing
  confidence into measured model calibration. Preserve historical runs and label
  them with their original parser version rather than silently rescoring them.
- Request constrained JSON where supported and validate independently. Reject
  duplicate keys, non-finite numbers, extra prose, wrong types, and truncated
  outputs. Ordinary mentor prose remains a text response, with finish status.
- Move the compact and transfer benchmark clients behind the shared provider
  interface through an adapter preserving their existing fixture behavior.
- Keep Needle out of automatic learner-score or evidence repair. Optional draft
  extraction must retain original text and require review of changed values.

**Acceptance:** the general provider and both benchmark paths agree on malformed
response outcomes. NaN, infinity, missing probabilities, contradictory fields,
and truncation cannot enter scored rows as normal answers. Failed runs retain
their denominator and failure reason. Existing valid fixtures and explicit demo
behavior remain supported.

### DD-3 — qualify roles with independent evidence (P0 reporting, P1 evaluation)

Correct heuristic labels and circular metric exports immediately; those
reporting repairs do not require a live model. Live qualification depends on
DD-1–DD-2. Reuse [model_bench](local-model-benchmark.md),
[arena](arena.md), and the [AI-learner plan](ai-learner-mentorship-benchmark.md).

1. Label existing keyword scores as response-shape heuristics. Keep them for fast
   smoke checks; prevent their rating from being interpreted as independently
   established teaching quality or claim truth. Preserve legacy export fields
   with a documented migration and assessment-type label.
2. Build at least 30 reviewed role cases, initially ten each for mentor,
   practice, and evaluator. Include correct and incorrect answers, existing
   caveats, insufficient evidence, misleading source instructions, and tempting
   answer leakage. Hold out at least one-third before tuning. Broader languages
   and domains require their own reviewed slices.
3. Compare Q4, Q2, and IQ3 on identical source bundles, prompts, budgets, and
   repeated trials. Use the deterministic session as a baseline. Review factual
   support, source anchors, useful hints, exercise solvability, preservation of
   learner caveats, invented criticism, and leakage of full solutions.
4. Use independently reviewed labels for correctness/calibration. Have the
   evaluator cite the learner span and source passage behind each criticism.
   Keep heuristic behavior scores, answer probabilities, evidence coverage,
   and mastery measures separate under the existing Epistemap contract.
5. Extend the existing source-blind pretest, source exposure, transfer, and
   retention-proxy experiments to the selected backends. Record answer-key
   access, intervention conditions, model/prompt hashes, and self-evaluation.
   AI-learner gains remain research evidence; human benefit needs a human pilot.

**Acceptance:** the three keyword-only probes above cannot qualify a mentor.
Publish per-case outcomes, disagreement/adjudication, sample sizes, failed-call
counts, latency distributions, and uncertainty. Critical fixed cases must have
no fabricated source anchors, invented missing caveats, or unauthorized mastery
changes. Select a model per task only where held-out quality and latency support
the choice; retain reviewed use when the sample is insufficient.

### DD-4 — make multi-turn interaction responsive and recoverable (P1/P2)

Depends on DD-1–DD-2; tuning should use DD-3's quality measurements.

- Measure model loading/hash checks, queue wait, prompt processing, decode,
  validation, and full turn time separately. Preserve existing pending notices.
  Add time-to-first-token only where streaming is actually implemented.
- Retain compact, source-anchored context and the current short response budgets.
  Detect context overflow explicitly. Evaluate streaming for mentor prose after
  finish/error handling is sound; structured records remain provisional until
  complete validation.
- Reuse existing atomic session persistence. Add per-turn completion/failure
  records and bounded retry so one timeout does not require repeating accepted
  turns. Record the original route and any explicit fallback model.
- Start with one resident model per worker and one request slot. Avoid switching
  Q2 and IQ3 between every role. Put longer ingestion/evaluation batches behind
  interactive turns and measure fairness before increasing concurrency.
- Surface an unavailable tutor as unavailable, with an explicit deterministic
  activity option. Do not substitute a stub while presenting live assistance.

**Acceptance:** interrupt after a completed turn and resume without duplicating
learner evidence or overwriting an accepted response. Timeout, cancellation,
context overflow, and failed validation have visible states. A short-turn pilot
reports median and tail latency under stated load; its latency target is chosen
before comparing models and never substitutes for DD-3's quality gate.

### DD-5 — verify the citation-to-learning handoff (P1)

Coordinate with CiteGeist CG-2; review the existing
[citation extractor](../src/didactopus/citation_extract.py) before adding fields.
It already preserves source/fragment IDs, draft status, and render errors.

- Version the handoff for source fragments, citation occurrences, candidate work
  identity, resolver provenance, metadata conflicts, support-review state, and
  explicit failures. Maintain the distinction between finding a citation and
  finding evidence that supports a claim.
- Preserve missing references and rendering failures as reviewable artifacts.
  An unavailable CiteGeist backend must not become a completed citation review.
- Verify imports do not promote bibliography candidates, claim support, or
  learner mastery. Keep private learner submissions and restricted source text
  outside general retrieval and public exports.
- Add paired producer/consumer fixtures for unresolved works, conflicting
  editions, missing anchors, malformed records, and partial backend failure.

**Acceptance:** the same handoff fixtures pass in both repositories. A generated
placeholder cannot arrive as a verified source; rejected or unresolved records
stay visible. Public export checks preserve allowed provenance without including
private raw prompts or learner responses.

### DD-6 — keep documentation and acceptance checks truthful (P1, ongoing)

- Extend existing CI rather than creating another runner. Exercise every shipped
  provider example and distinguish offline tests, explicit demos, optional live
  smoke checks, and required model-qualification runs.
- Update [provider setup](model-provider-setup.md) with implemented capabilities
  and URL/authentication conventions. Link the chosen task-qualified profiles
  only after the corresponding evaluation is complete.
- Publish status per role: configured, transport-tested, fixture-tested,
  model-evaluated, reviewed pilot, adopted. Track each status with evidence.
- Add a benchmark manifest schema carrying parser/scorer versions, model weights
  and runtime revision, source bundle, sampling settings, context/output budgets,
  host, and failure counts. Keep learner records private by default.

**Acceptance:** a documented live path cannot pass through a stub unnoticed.
Benchmark reports cannot omit invalid cases or present heuristic labels as
independent correctness judgments. Each roadmap completion links to its checks.

## Coordination and first changes

The first three changes should be **DD-1 explicit provider dispatch**,
**DD-2 strict benchmark-result validation**, and **DD-3 honest heuristic-score
labels plus reviewed role fixtures**. Add regression tests for the confirmed
failures with their fixes. No model download is required to start these changes.

The [main roadmap](roadmap.md) remains the entry point. The
[educational graph plan](educational-graph-correction-roadmap.md) retains its
own DG-1–DG-5 scope and October demo sequence; this plan does not reschedule it.
Graph diagnostics must pass their own gates before serving as trusted context
in a model evaluation. Existing pedagogy and learner-evidence foundations remain
in place. The [GroundRecall companion plan](groundrecall-unified-retrieval-integration-plan.md)
retains its separate store-reconciliation dependency.

Share JSON failure fixtures and citation-handoff contracts with CiteGeist.
Prefer a small versioned library contract or matching fixtures over introducing
a new central service before both consumers need one. Keep CiteGeist responsible
for bibliographic identity and Didactopus responsible for educational review.

Retain the existing preferred model registry, pinned llama.cpp runtime, and
gorlim's full weight-hash verification. Needle remains experimental on nerdanel
and unqualified on pallando. Neither CPU classifier accuracy nor JSON validity
establishes factual correctness, instructional value, or learner mastery.
