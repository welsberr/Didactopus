# Evaluator Pipeline

The evaluator pipeline converts learner attempts into mastery evidence.

Flow:

1. learner attempt
2. evaluators score attempt
3. scores aggregated by dimension
4. assessment stored as draft evidence with provenance and review state
5. approved evidence promoted into the mastery ledger

The Notebook learner-session path implements steps 1-4 without silently
performing step 5. Its deterministic assessment and evaluator response are
review inputs. Human learner attempts remain `draft`, AI-learner attempts are
`benchmark_only`, and both declare `mastery_effect=none_until_review` until an
explicit promotion workflow applies a typed mastery event.

Evaluator types:

• rubric
• code/test
• symbolic rule
• critique
• portfolio
