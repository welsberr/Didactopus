# Reasoning Scaffold Operations

Didactopus should treat reviewed reasoning scaffolds as instructional inputs, not as hidden model reasoning. A scaffold record is useful when it gives a learner-facing question, a concise answer summary, an evidence check, and a misconception guard that can be turned into a learning action.

The broader operational policy for mentor sessions is in
[mentoring-operational-process.md](mentoring-operational-process.md). This file
describes how reasoning scaffolds plug into that process.

This should have operational consequences inside mentorship flows. A reviewed
scaffold should influence:

- the first question a mentor asks
- which evidence check is emphasized
- which misconception risk is surfaced early
- how the learner is asked to revise or extend an answer

## Consumption Rules

- Use `didactopus_prompt_seed` fields as prompt material for prediction, evidence comparison, reflection, and revision.
- Keep the learner focused on observable claims: what was predicted, what evidence appeared, what alternative explanation remains possible, and what should be revised.
- Preserve provenance. When a scaffold points to a Notebook page, app, pack, source note, or bibliography slot, keep that link visible in generated activities.
- Do not ask learners to reproduce raw chain-of-thought. Ask for short public reasoning products: claim, evidence, uncertainty, alternative, and revision.
- Treat missing citations as an explicit limitation until CiteGeist or another reviewed source workflow resolves the source slot.
- Treat scaffold records as reviewed public reasoning aids, not as static
  metadata attached to a page.
- Keep summary, analysis, worked example, practice prompt, and evaluator
  judgment distinct in mentor output.
- Treat fallacy cues, claim alignments, and lineage suggestions as review
  tasks unless they have already been promoted through GroundRecall.

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

- `notebook/concepts/allele-frequency-change.scaffold.json`
- `notebook/concepts/allele-frequency-change.html`

Use it as the reference fixture for future pack and learner-session integrations.

The current Notebook path-level input is:

- `notebook/learning-paths/foundations-first-ring.didactopus.json`

Use that artifact when the goal is not just "consume one scaffold record" but
"run a reviewed concept sequence with mentor openings and transition cues
already attached."

## Learning Sequence Input

When a Didactopus-facing learning-sequence artifact is available, treat it as a
path contract between the Notebook and mentorship flow.

Preferred fields include:

- `sequence`
- per-step `concept_id`
- per-step `title`
- per-step `url`
- per-step `session_goal`
- per-step `mentor_opening`
- per-step `evidence_focus`
- per-step `next_transition`

Operationally, that means:

- the Notebook determines the current recommended concept order
- the sequence artifact determines how Didactopus should open and hand off each
  session
- individual scaffold records still supply concept-local question, answer,
  verification, and misconception material

This keeps path selection, concept scaffolding, and mentorship behavior aligned
without making Didactopus the owner of Notebook sequencing.

The current thin consumer path is:

```bash
PYTHONPATH=src python3 -m didactopus.main sequence-plan \
  --sequence notebook/learning-paths/foundations-first-ring.didactopus.json
```

That emits a deterministic mentorship-oriented session plan from the reviewed
Notebook sequence contract.

The next consumer layer is the learner-session demo itself:

```bash
PYTHONPATH=src python3 -m didactopus.learner_session_demo \
  --sequence notebook/learning-paths/foundations-first-ring.didactopus.json \
  --step-index 0
```

That uses one reviewed Notebook sequence step as the grounding source for the
mentor/practice/evaluator/next-step flow while preserving the existing session
payload shape.

## Verification Note

When testing local `Didactopus` changes that touch scaffold consumption or
learner-session behavior, prefer running tests against the checkout source tree:

```bash
PYTHONPATH=src python3 -m pytest tests/test_learner_session.py
```

This avoids accidentally importing an older editable install from another local
checkout.
