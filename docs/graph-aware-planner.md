# Graph-Aware Planner

The graph-aware planner ranks next concepts using a transparent utility model.

## Inputs

- concept graph
- learner mastery state
- evidence summaries
- target concepts
- semantic similarity estimates
- project catalog

## Current scoring terms

- **readiness_bonus**: concept is currently studyable
- **target_distance_weight**: closer concepts to the target score higher
- **weak_dimension_bonus**: concepts with known weakness signals are prioritized
- **fragile_review_bonus**: resurfaced or fragile concepts are review-prioritized
- **project_unlock_bonus**: concepts that unlock projects score higher
- **semantic_similarity_weight**: concepts semantically close to targets gain weight

## Future work

- learner time budgets
- spaced repetition costs
- multi-objective planning
- planning across multiple targets
- reinforcement learning over curriculum policies
