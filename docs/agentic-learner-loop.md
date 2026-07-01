# Agentic Learner Loop

The agentic learner loop is the first closed-loop prototype for AI-student behavior in Didactopus.

## Current loop

1. Inspect current mastery state
2. Ask graph-aware planner for next best concept
3. Retrieve reviewed source fragments, scaffolds, study-aid records, and
   relevant recent learner evidence
4. Orient the learner with a source-spine frame and a bounded prompt
5. Produce or collect a learner attempt
6. Score attempt into evidence
7. Return feedback that separates source summary, mentor interpretation, and
   evaluator judgment
8. Update mastery state, misconception observations, source-support gaps, and
   next-step recommendation
9. Repeat until target is reached or iteration budget ends

## Important limitation

The current implementation is a scaffold. The learner attempt is synthetic and deterministic, not a true external model call with robust domain evaluation.

## Why it still matters

It establishes the orchestration pattern for:
- planner-guided concept selection
- evidence accumulation
- mastery updates
- goal-directed progression
- study-aid use without source replacement
- worked-example, faded-example, and retrieval-practice turns
- argument and citation mentoring with reviewed provenance

## Mentoring Contract

The loop should implement the process in
[mentoring-operational-process.md](mentoring-operational-process.md). In
particular, mentor, practice, and evaluator roles should avoid answer
offloading, preserve provenance, and treat fallacy cues, claim alignments, and
lineage suggestions as reviewable tasks rather than automatic conclusions.

## AI Learner Evaluation

The synthetic learner path should evolve toward the benchmark design in
[ai-learner-mentorship-benchmark.md](ai-learner-mentorship-benchmark.md). A real
AI-learner run should:

- use a local model through the provider boundary;
- begin with a source-blind pretest;
- require confidence or probability estimates for scored claims;
- run a source-grounded mentoring intervention;
- evaluate parallel posttest and transfer probes;
- export `scored_claims.csv` for practical `G` estimation;
- keep AI learner evidence separate from human learner mastery evidence.
