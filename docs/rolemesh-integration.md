# Gateway Integration

Didactopus now treats a generic OpenAI-compatible gateway as the main local-LLM
integration boundary.

GenieHive is the primary recommended backend for that boundary because it
already provides:

- `GET /v1/models`
- `POST /v1/chat/completions`
- route resolution over healthy loaded services
- role-addressable model aliases
- service and health inspection APIs

## Recommended architecture

1. Run GenieHive control as the OpenAI-compatible front door.
2. Expose the model aliases or role aliases you want from GenieHive.
3. Configure Didactopus to use the `geniehive` model provider.
4. Map Didactopus roles to GenieHive model or role aliases in `role_to_model`.
5. Let Didactopus send role-specific requests while GenieHive handles routing.

## Didactopus-side config

Use `configs/config.geniehive.example.yaml` as the starting point.

Important fields:

- `model_provider.provider: geniehive`
- `model_provider.geniehive.base_url`
- `model_provider.geniehive.api_key`
- `model_provider.geniehive.default_model`
- `model_provider.geniehive.role_to_model`

## Canonical Didactopus roles

Didactopus defines its own role ids in code and expects the gateway layer to map
them to service aliases.

Current canonical roles:

- `mentor`
- `learner`
- `practice`
- `project_advisor`
- `evaluator`

For AI-learner benchmarks, map `learner` deliberately to the model under test.
Do not reuse the mentor or evaluator model as the learner unless the run is
explicitly marked as self-evaluated. The evaluator should usually be stronger
or should be backed by deterministic checks and reviewed answer keys.

The example GenieHive config maps those roles to:

- `mentor -> planner`
- `learner -> writer`
- `practice -> writer`
- `project_advisor -> planner`
- `evaluator -> reviewer`

Change only the right-hand side values to fit your local GenieHive role or
model aliases.

## AI Learner Benchmark Use

The gateway boundary is the right place to run local GPU models for the
AI-learner mentorship benchmark described in
[ai-learner-mentorship-benchmark.md](ai-learner-mentorship-benchmark.md).

Recommended practice:

- inspect healthy routes before each run;
- record route resolution in the benchmark manifest;
- map smaller models to `learner`;
- map stronger or more reliable models to `mentor` and `evaluator`;
- keep answer keys out of learner prompts;
- preserve full prompts, settings, and model ids for replay.

## Demo commands

Stubbed local-provider demo:

```bash
python -m didactopus.gateway_demo --config configs/config.example.yaml
```

GenieHive-backed example config:

```bash
python -m didactopus.gateway_demo --config configs/config.geniehive.example.yaml
```

MIT OCW learner transcript through the local-LLM path:

```bash
python -m didactopus.ocw_provider_transcript_demo --config configs/config.geniehive.example.yaml
```

If local inference is slow, the transcript demo emits pending notices while each
turn is running. For a full manual capture, run:

```bash
python -u -m didactopus.ocw_provider_transcript_demo \
  --config configs/config.geniehive.example.yaml \
  --out-dir examples/ocw-information-entropy-provider-transcript \
  2>&1 | tee examples/ocw-information-entropy-provider-transcript/manual-run.log
```

That gives you:

- `provider_transcript.json`
- `provider_transcript.md`
- `manual-run.log`

## Compatibility note

The older `rolemesh` provider name and RoleMesh-named demo modules are still
available as compatibility wrappers. They should be treated as legacy entry
points while the codebase and docs converge on the provider-neutral gateway
surface.
