# RoleMesh Integration

RoleMesh Gateway is an appropriate dependency for local-LLM-backed Didactopus usage.

## Why it fits

The local RoleMesh codebase provides exactly the main things Didactopus needs for a local heterogeneous inference setup:

- OpenAI-compatible `POST /v1/chat/completions`
- role-based model routing
- local or multi-host upstream registration
- flexible model loading and switching through the gateway/node-agent split
- per-role defaults for temperature and other request settings

That means Didactopus can keep a simple provider abstraction while delegating model placement and routing to RoleMesh.

## Recommended architecture

1. Run RoleMesh Gateway as the OpenAI-compatible front door.
2. Point RoleMesh roles at local backends or discovered node agents.
3. Configure Didactopus to use the `rolemesh` model provider.
4. Let Didactopus send mentor/practice/project-advisor/evaluator requests by role.

## Didactopus-side config

Use `configs/config.rolemesh.example.yaml` as the starting point.

The important fields are:

- `model_provider.provider: rolemesh`
- `model_provider.rolemesh.base_url`
- `model_provider.rolemesh.api_key`
- `model_provider.rolemesh.default_model`
- `model_provider.rolemesh.role_to_model`

## Suggested role mapping

With the sample RoleMesh gateway config, this is a good default mapping:

- `mentor -> planner`
- `practice -> writer`
- `project_advisor -> planner`
- `evaluator -> reviewer`

This keeps Didactopus prompts aligned with the role semantics RoleMesh already exposes.

## Prompt layer

Didactopus now keeps its default RoleMesh-oriented prompts in:

- `didactopus.role_prompts`

These prompts are intentionally anti-offloading:

- mentor mode prefers Socratic questions and hints
- practice mode prefers reasoning-heavy tasks
- project-advisor mode prefers synthesis work
- evaluator mode prefers critique and explicit limitations

## Demo command

To exercise the integration path without a live RoleMesh gateway, run:

```bash
python -m didactopus.rolemesh_demo --config configs/config.example.yaml
```

That uses the stub provider path.

To point at a live RoleMesh deployment, start from:

```bash
python -m didactopus.rolemesh_demo --config configs/config.rolemesh.example.yaml
```

and replace the placeholder gateway URL/API key with your real local setup.

## Example transcript

The repository now includes a generated transcript of an AI learner using the local-LLM path to approach the MIT OCW Information and Entropy course:

- `examples/ocw-information-entropy-rolemesh-transcript/rolemesh_transcript.md`

Generator command:

```bash
python -m didactopus.ocw_rolemesh_transcript_demo --config configs/config.rolemesh.example.yaml
```

If some RoleMesh aliases are unhealthy, the transcript demo automatically falls back to the healthy local alias and records that in the output metadata.

If local inference is slow, the transcript demo now emits pending notices such as “Didactopus is evaluating the work before replying” while each turn is still running. For a full manual capture, run:

```bash
python -u -m didactopus.ocw_rolemesh_transcript_demo \
  --config configs/config.rolemesh.example.yaml \
  --out-dir examples/ocw-information-entropy-rolemesh-transcript \
  2>&1 | tee examples/ocw-information-entropy-rolemesh-transcript/manual-run.log
```

That gives you three artifacts:

- `rolemesh_transcript.json`
- `rolemesh_transcript.md`
- `manual-run.log` with the live “pending” status messages

For slower larger models, expect the transcript run to take several minutes rather than seconds. The command above is the recommended way to capture the whole session outside Codex.

## Gateway-side note

This repository does not vendor RoleMesh. It assumes the local RoleMesh codebase or deployment exists separately. The reference local codebase mentioned by the user is suitable because it already provides the API and routing semantics Didactopus needs.
