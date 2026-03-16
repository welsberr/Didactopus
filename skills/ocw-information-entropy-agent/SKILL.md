---
name: ocw-information-entropy-agent
description: Use the generated MIT OCW Information and Entropy pack, concept ordering, and learner artifacts to mentor or evaluate information-theory work.
---

# OCW Information Entropy Agent

Use this skill when the task is about tutoring, evaluating, or planning study in Information Theory using the generated MIT OCW 6.050J pack.

## Workflow

1. Read `references/generated-course-summary.md` for the pack structure and target concepts.
2. Read `references/generated-capability-summary.md` to understand what the deterministic demo learner already mastered.
3. Use `assets/generated/pack/` as the source of truth for concept ids, prerequisites, and mastery signals.
4. Use `assets/generated/pack/source_corpus.json` to ground explanations in the ingested source material before relying on model prior knowledge.
5. When giving guidance, preserve the pack ordering from fundamentals through coding and thermodynamics.
6. When uncertain, say which concept or prerequisite in the generated pack is underspecified and which source fragment would need review.

## Outputs

- study plans grounded in the pack prerequisites
- concept explanations tied to entropy, coding, and channel capacity
- evaluation checklists using the generated capability report
- follow-up exercises that extend the existing learner artifacts
- local-LLM tutoring or evaluation runs that use the same pack and source corpus through role-based prompts
