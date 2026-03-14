# Data Model Outline

## New core entities

### KnowledgeCandidate
```json
{
  "candidate_id": "kc_001",
  "source_type": "learner_export",
  "source_artifact_id": 42,
  "learner_id": "learner_a",
  "pack_id": "stats_intro",
  "candidate_kind": "hidden_prerequisite",
  "title": "Variance may be an unstated prerequisite for standard deviation",
  "summary": "Learner evidence suggests an implicit conceptual dependency.",
  "structured_payload": {},
  "evidence_summary": "Repeated low-confidence performance.",
  "confidence_hint": 0.72,
  "novelty_score": 0.61,
  "synthesis_score": 0.58,
  "triage_lane": "pack_improvement",
  "current_status": "triaged"
}
```

### ReviewRecord
```json
{
  "review_id": "rv_001",
  "candidate_id": "kc_001",
  "reviewer_id": "mentor_1",
  "review_kind": "human_review",
  "verdict": "accept_pack_improvement",
  "rationale": "Supported by learner evidence and pack topology."
}
```

### PromotionRecord
```json
{
  "promotion_id": "pr_001",
  "candidate_id": "kc_001",
  "promotion_target": "pack_improvement",
  "target_object_id": "patch_014",
  "promotion_status": "approved"
}
```

### SynthesisCandidate
```json
{
  "synthesis_id": "syn_001",
  "source_concept_id": "entropy_info",
  "target_concept_id": "entropy_thermo",
  "source_pack_id": "information_theory",
  "target_pack_id": "thermodynamics",
  "synthesis_kind": "cross_pack_similarity",
  "score_total": 0.84,
  "score_semantic": 0.88,
  "score_structural": 0.71,
  "score_trajectory": 0.55,
  "score_review_history": 0.60,
  "explanation": "These concepts share terminology and play analogous explanatory roles."
}
```
