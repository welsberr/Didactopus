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
2. Expose whatever model aliases or upstream routes you want from RoleMesh Gateway.
3. Configure Didactopus to use the `rolemesh` model provider.
4. Map Didactopus roles to RoleMesh model aliases in `role_to_model`.
5. Let Didactopus send role-specific requests while RoleMesh handles the actual model routing.

## Didactopus-side config

Use `configs/config.rolemesh.example.yaml` as the starting point.

The important fields are:

- `model_provider.provider: rolemesh`
- `model_provider.rolemesh.base_url`
- `model_provider.rolemesh.api_key`
- `model_provider.rolemesh.default_model`
- `model_provider.rolemesh.role_to_model`

## Canonical Didactopus roles

Didactopus now defines its own role set in code. RoleMesh is expected to serve those roles by alias mapping rather than by imposing its own role vocabulary.

Current canonical roles:

- `mentor -> planner`
- `learner -> writer`
- `practice -> writer`
- `project_advisor -> planner`
- `evaluator -> reviewer`

These are the default RoleMesh alias values in the example config, not required gateway role names.

The Didactopus role meanings are:

- `mentor`: sequencing, hints, conceptual framing, and prerequisite guidance
- `learner`: learner-side reflection or transcript voice
- `practice`: exercise generation without answer offloading
- `project_advisor`: synthesis work and capstone-style guidance
- `evaluator`: critique, limitation checks, and mastery-oriented feedback

## Default alias mapping

The example config maps those Didactopus roles to these RoleMesh aliases:

- `mentor -> planner`
- `learner -> writer`
- `practice -> writer`
- `project_advisor -> planner`
- `evaluator -> reviewer`

That mapping is only a starting point. If your RoleMesh deployment uses aliases like `didactopus-mentor`, `study-writer`, or `local-critic`, change only the right-hand side values in `role_to_model`.

## How to customize it

`role_to_model` is the main integration seam.

Example:

```yaml
model_provider:
  provider: rolemesh
  rolemesh:
    base_url: "http://127.0.0.1:8000"
    api_key: "change-me-client-key-1"
    default_model: "didactopus-mentor"
    role_to_model:
      mentor: "didactopus-mentor"
      learner: "didactopus-learner"
      practice: "didactopus-practice"
      project_advisor: "didactopus-projects"
      evaluator: "didactopus-evaluator"
```

Recommended rules for changes:

- Keep the left-hand side role ids unchanged unless you are also changing Didactopus code.
- Change the right-hand side values freely to match your local RoleMesh aliases.
- If two Didactopus roles can share one model, map them to the same alias.
- If one role needs a stronger or more cautious model, give it a dedicated alias in RoleMesh and map it here.

If you want to add a brand-new Didactopus role, update:

- `src/didactopus/roles.py`
- `src/didactopus/role_prompts.py`
- any feature module that calls `provider.generate(..., role=...)`
- `configs/config.rolemesh.example.yaml`

## Prompt layer

Didactopus keeps its role prompts in:

- `didactopus.role_prompts`
- `didactopus.roles`

These prompts are intentionally anti-offloading:

- mentor mode prefers Socratic questions and hints
- learner mode preserves an earnest learner voice rather than a solver voice
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
