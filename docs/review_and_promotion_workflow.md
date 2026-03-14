# Review-and-Promotion Workflow for Learner-Derived Knowledge

## Purpose

Learner-derived knowledge should move through a controlled path from raw
observation to reusable system asset. This workflow is designed to turn exports
into reviewed candidates that can become:

- accepted pack improvements
- curriculum drafts
- reusable skill bundles
- archived but unadopted suggestions

## Design goals

- preserve learner discoveries without assuming correctness
- support reviewer triage and provenance
- separate candidate knowledge from accepted knowledge
- allow multiple promotion targets
- keep enough traceability to understand why a candidate was accepted or rejected

---

## Workflow stages

### 1. Capture
Input sources include:

- learner knowledge exports
- mentor observations
- evaluator traces
- synthesis-engine proposals
- artifact-derived observations

Output:
- one or more **knowledge candidates**

### 2. Normalize
Convert raw export text and metadata into structured candidate records, such as:

- concept observation
- hidden prerequisite suggestion
- misconception note
- analogy / cross-pack link suggestion
- curriculum draft fragment
- skill-bundle candidate

### 3. Triage
Each candidate is routed into a review lane:

- pack improvement
- curriculum draft
- skill bundle
- archive / backlog

Triage criteria:
- relevance to existing packs
- novelty
- evidence quality
- reviewer priority
- confidence / ambiguity

### 4. Review
Human or automated reviewers inspect the candidate.

Reviewer questions:
- is the claim coherent?
- is it genuinely new or just a restatement?
- does evidence support it?
- does it fit one or more promotion targets?
- what are the risks if promoted?

### 5. Decision
Possible outcomes:

- accept into pack improvement queue
- promote to curriculum draft
- promote to skill bundle draft
- archive but keep discoverable
- reject as invalid / duplicate / unsupported

### 6. Promotion
Accepted items are transformed into target-specific assets:

- pack patch proposal
- curriculum draft object
- skill bundle object

### 7. Feedback and provenance
Every decision stores:

- source export
- source learner
- source pack
- reviewer identity
- rationale
- timestamps
- superseding links if a later decision replaces an earlier one

---

## Target lanes

## A. Accepted pack improvements

Typical promoted items:
- missing prerequisite
- poor concept ordering
- missing example
- misleading terminology
- clearer analogy
- cross-pack link worth formalizing

Output objects:
- patch proposals
- revised concept metadata
- candidate new edges
- explanation replacement suggestions

Recommended fields:
- pack_id
- concept_ids_affected
- patch_type
- proposed_change
- evidence_summary
- reviewer_notes
- promotion_status

## B. Curriculum drafts

Typical promoted items:
- lesson outline
- concept progression plan
- exercise cluster
- misconceptions guide
- capstone prompt
- study guide segment

Output objects:
- draft lessons
- outline sections
- teacher notes
- question banks

Recommended fields:
- curriculum_product_type
- topic_focus
- target audience
- prerequisite level
- source concepts
- generated draft
- editorial notes

## C. Reusable skill bundles

Typical promoted items:
- concept mastery checklist
- canonical examples
- error patterns
- prerequisite structure
- evaluation rubrics
- recommended actions

Output objects:
- skill manifest
- skill tests
- skill examples
- operational notes

Recommended fields:
- skill_name
- target domain
- prerequisites
- expected inputs
- failure modes
- validation checks
- source pack links

## D. Archived but unadopted suggestions

Some observations should remain searchable even if not promoted.

Use this lane when:
- evidence is interesting but incomplete
- idea is plausible but low priority
- reviewer is uncertain
- concept does not fit a current roadmap
- duplication risk exists but insight might still help later

Recommended fields:
- archive_reason
- potential_future_use
- reviewer_notes
- related packs
- revisit_after

---

## Core data model

### KnowledgeCandidate
- candidate_id
- source_type
- source_artifact_id
- learner_id
- pack_id
- candidate_kind
- title
- summary
- structured_payload
- evidence_summary
- confidence_hint
- novelty_score
- synthesis_score
- triage_lane
- current_status
- created_at

### ReviewRecord
- review_id
- candidate_id
- reviewer_id
- review_kind
- verdict
- rationale
- requested_changes
- created_at

### PromotionRecord
- promotion_id
- candidate_id
- promotion_target
- target_object_id
- promotion_status
- promoted_by
- created_at

### CandidateLink
- link_id
- candidate_id
- related_candidate_id
- relation_kind
- note

---

## Suggested states

Candidate states:
- captured
- normalized
- triaged
- under_review
- accepted
- promoted
- archived
- rejected

Pack improvement states:
- proposed
- approved
- merged
- superseded

Curriculum draft states:
- draft
- editorial_review
- approved
- published

Skill bundle states:
- draft
- validation
- approved
- deployed

---

## Promotion rules

### Pack improvements
Promote when:
- directly improves pack clarity or structure
- supported by evidence or synthesis signal
- low risk of destabilizing pack semantics

### Curriculum drafts
Promote when:
- pedagogically useful even if not strictly a pack change
- enough material exists to support a lesson, guide, or exercise group

### Skill bundles
Promote when:
- insight can be operationalized into a reusable structured behavior package
- prerequisites, examples, and evaluation logic are sufficiently clear

### Archive
Use when:
- the idea is promising but under-evidenced
- better future context may make it valuable
- reviewer wants traceability without immediate adoption

---

## Review UX recommendations

Reviewer interface should show:

- candidate summary
- source artifact and export trace
- related concepts and packs
- novelty score
- synthesis score
- suggested promotion targets
- side-by-side comparison with current pack text
- one-click actions for:
  - accept as pack improvement
  - promote to curriculum draft
  - promote to skill bundle
  - archive
  - reject

---

## Integration with synthesis engine

Synthesis proposals should enter the same workflow as learner-derived candidates.
This creates a unified promotion pipeline for:

- human observations
- AI learner observations
- automated synthesis discoveries
