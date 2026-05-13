# Reasoning Scaffold Operations

Didactopus should treat reviewed reasoning scaffolds as instructional inputs, not as hidden model reasoning. A scaffold record is useful when it gives a learner-facing question, a concise answer summary, an evidence check, and a misconception guard that can be turned into a learning action.

## Consumption Rules

- Use `didactopus_prompt_seed` fields as prompt material for prediction, evidence comparison, reflection, and revision.
- Keep the learner focused on observable claims: what was predicted, what evidence appeared, what alternative explanation remains possible, and what should be revised.
- Preserve provenance. When a scaffold points to a Notebook page, app, pack, source note, or bibliography slot, keep that link visible in generated activities.
- Do not ask learners to reproduce raw chain-of-thought. Ask for short public reasoning products: claim, evidence, uncertainty, alternative, and revision.
- Treat missing citations as an explicit limitation until CiteGeist or another reviewed source workflow resolves the source slot.

## Expected Record Fields

Didactopus can work with partial records, but the preferred shape is:

- `id`
- `type`
- `question`
- `answer_summary`
- `verification_prompt`
- `misconception_guard`
- `didactopus_prompt_seed`
- source or site links

## Example Source

The current evo-edu Notebook pilot is:

- `/home/netuser/dev/evo-edu.org/notebook/concepts/allele-frequency-change.scaffold.json`
- `/home/netuser/dev/evo-edu.org/notebook/concepts/allele-frequency-change.html`

Use it as the reference fixture for future pack and learner-session integrations.
