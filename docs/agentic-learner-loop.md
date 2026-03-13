# Agentic Learner Loop

The agentic learner loop is the first closed-loop prototype for AI-student behavior in Didactopus.

## Current loop

1. Inspect current mastery state
2. Ask graph-aware planner for next best concept
3. Produce synthetic attempt
4. Score attempt into evidence
5. Update mastery state
6. Repeat until target is reached or iteration budget ends

## Important limitation

The current implementation is a scaffold. The learner attempt is synthetic and deterministic, not a true external model call with robust domain evaluation.

## Why it still matters

It establishes the orchestration pattern for:
- planner-guided concept selection
- evidence accumulation
- mastery updates
- goal-directed progression
