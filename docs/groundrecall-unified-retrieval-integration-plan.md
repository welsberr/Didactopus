# GroundRecall Unified Retrieval: Didactopus Companion Plan

Status: draft for review; blocked on GroundRecall UPR-0 store reconciliation.

## Purpose

Didactopus should pilot GroundRecall evidence bundles as provenance-rich context
for mentor, steward, and development workflows. Retrieval must not become a
shortcut around pedagogy or a new learner-assessment signal.

The controlling roadmap is GroundRecall's
[`unified-prior-work-retrieval-roadmap.md`](../../GroundRecall/docs/unified-prior-work-retrieval-roadmap.md).
This plan is subordinate to Didactopus's learner-session and local-first
roadmap.

## Safety Boundary

- Retrieved prior work may orient a mentor or developer; it is not evidence of
  learner competence.
- Retrieval relevance, Epistemap reliability, learner response probability,
  mastery, and evidence coverage remain separate measures.
- Private learner responses, ledgers, diagnostics, and transcripts are not
  registered GroundRecall corpora and are not eligible for private replay.
- A context bundle must not reveal answers that invalidate an assessment or
  bypass a planned learning activity.

## Work Packages

### D-UR1: Documentation and query fixture

- Register selected public architecture, roadmap, mentoring-process, deployment,
  and pack-contract documentation at pinned Git revisions.
- Add synthetic questions for session resumption, current implementation state,
  design boundaries, and source-grounding behavior.
- Label expected material that is safe for mentor context versus steward-only or
  assessment-sensitive.

Acceptance: GroundRecall retrieves current documentation without mixing it with
private learner state or obsolete roadmap claims.

### D-UR2: Read-only bundle consumer

- Map GroundRecall bundle groups into bounded mentor/developer context with
  source references and selection reasons visible.
- Add an explicit policy filter for role, activity, and assessment sensitivity.
- Preserve weak, stale, superseded, and contradictory warnings.
- Retain deterministic behavior when GroundRecall or local embeddings are
  unavailable.

Acceptance: golden fixtures show that unsafe groups are omitted, omissions are
reported, and no retrieved item changes mastery or evidence state.

### D-UR3: Resumption evaluation

- Test interrupted developer and steward tasks first; learner-session recovery
  remains governed by Didactopus's existing private ledgers.
- Score recovery of objective, completed step, current decision, constraint,
  blocker, and next action.
- Compare no recall, lexical bundle, and local-hybrid bundle conditions without
  exposing private learner text.

Acceptance: resumption improves over the baseline without substantial user
re-orientation, privacy leakage, or pedagogical answer disclosure.

## Dependencies and Non-Goals

- No code work before GroundRecall UPR-0 passes.
- Bundle consumption follows GroundRecall UPR-2; hybrid comparison follows
  UPR-3; recovery evaluation follows UPR-4.
- Didactopus does not own GroundRecall ranking, embeddings, canonical memory,
  recovery segments, or cross-repository corpus registration.

