# Model Provider Setup

Didactopus now supports three main model-provider paths:

- `ollama`
  - easiest local setup for most single users
- `openai_compatible`
  - simplest hosted setup when you want a common online API
- `rolemesh`
  - more flexible routing for technically oriented users, labs, and libraries

## Recommended Order

For ease of adoption, use these in this order:

1. `ollama`
2. `openai_compatible`
3. `rolemesh`

## Option 1: Ollama

This is the easiest local path for most users.

Use:

- `configs/config.ollama.example.yaml`

Minimal setup:

1. Install Ollama.
2. Pull a model you want to use.
3. Start or verify the local Ollama service.
4. Point Didactopus at `configs/config.ollama.example.yaml`.

Example commands:

```bash
ollama pull llama3.2:3b
python -m didactopus.learner_session_demo --config configs/config.ollama.example.yaml
```

If you want a different local model, change:

- `model_provider.ollama.default_model`
- `model_provider.ollama.role_to_model`

Use one model for every role at first. Split roles only if you have a reason to do so.

## Option 2: OpenAI-compatible hosted service

This is the easiest hosted path.

Use:

- `configs/config.openai-compatible.example.yaml`

This works for:

- OpenAI itself
- any hosted service that accepts OpenAI-style `POST /v1/chat/completions`

Typical setup:

1. Create a local copy of `configs/config.openai-compatible.example.yaml`.
2. Set `base_url`, `api_key`, and `default_model`.
3. Keep one model for all roles to start with.

Example:

```bash
python -m didactopus.learner_session_demo --config configs/config.openai-compatible.example.yaml
```

## Option 3: RoleMesh Gateway

RoleMesh is still useful, but it is no longer the easiest path to recommend to most users.

Choose it when you need:

- role-specific routing
- multiple local or remote backends
- heterogeneous compute placement
- a shared service for a library, lab, or multi-user setup

See:

- `docs/rolemesh-integration.md`

## Which commands use the provider?

Any Didactopus path that calls the model provider can use these configurations, including:

- `python -m didactopus.learner_session_demo`
- `python -m didactopus.rolemesh_demo`
- `python -m didactopus.model_bench`
- `python -m didactopus.ocw_rolemesh_transcript_demo`

The transcript demo name still references RoleMesh because that was the original live-LLM path, but the general learner-session and benchmark flows are the easier places to start.

## Practical Advice

- Start with one model for all roles.
- Prefer smaller fast models over bigger slow ones at first.
- Use the benchmark harness before trusting a model for learner-facing guidance.
- Use RoleMesh only when you actually need routing or multi-model orchestration.
