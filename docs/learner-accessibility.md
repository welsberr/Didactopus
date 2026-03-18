# Learner Accessibility

Didactopus should make the learner loop usable without assuming visual graph navigation or silent waiting on slow local models.

The current accessibility baseline is built on the graph-grounded learner session backend.

## Current Outputs

Running:

```bash
python -m didactopus.learner_session_demo
```

now writes:

- `examples/ocw-information-entropy-session.json`
- `examples/ocw-information-entropy-session.html`
- `examples/ocw-information-entropy-session.txt`

## What The Accessible Outputs Do

The HTML output is meant to be screen-reader-friendly and keyboard-friendly:

- skip link to the main content
- semantic headings
- reading-order sections for study plan, conversation, and evaluation
- grounded source fragments rendered as ordinary text instead of only visual diagrams
- deterministic learner-facing labels localized for supported output languages

The plain-text output is a linearized learner-session transcript that is suitable for:

- terminal reading
- screen-reader reading
- low-bandwidth sharing
- future text-to-speech pipelines

## Why This Matters

Didactopus should help learners work with structure, not just with pictures and dashboards.

This is especially important for:

- blind learners
- screen-reader users
- learners on low-power hardware
- situations where audio or text needs to be generated locally

## Relationship To The Roadmap

This is the accessibility baseline, not the endpoint.

Likely next steps:

- local text-to-speech for mentor, practice, and evaluator turns
- speech-to-text for learner answers
- explicit spoken structural cues
- text-first alternatives for more generated visualizations
