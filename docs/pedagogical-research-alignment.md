# Pedagogical Research Alignment

This note maps established learning-science findings to concrete Didactopus
design choices for source-grounded mentoring, AI learner benchmarks, and human
pilot work. It is meant to guide implementation, not to serve as a full
literature review.

## Research Threads To Preserve

Retrieval practice:

- Use closed-book or notes-only posttests after mentoring, not source-visible
  rereading tests.
- Include delayed retention probes. Immediate fluency is not enough evidence.
- Keep retrieval questions as first-class artifacts with answer keys and source
  anchors.

Worked examples and fading:

- Start novices with worked examples that make the target reasoning explicit.
- Fade later examples by removing one step at a time, then require the learner
  to complete the missing source-support, inference, or uncertainty step.
- Separate worked examples from summaries so the system can measure whether
  examples add value beyond content exposure.

Feedback:

- Feedback should answer three questions: where the learner is going, how the
  attempt compares with the target, and what the next step is.
- Feedback must distinguish source fact, mentor inference, evaluator judgment,
  and unresolved evidence.
- For argument work, feedback should identify the specific failed distinction:
  wrong source fact, unsupported causal inference, overgeneralization, missing
  confound, bad claim alignment, or poor calibration.

Confidence calibration and metacognition:

- Require true/false/unknown plus confidence for assessed claims.
- Treat correct low-confidence answers differently from calibrated mastery.
- Penalize overconfident wrong answers, unsupported source-blind answers, and
  fabricated citations or quotations.
- Record "what evidence would decide this?" prompts when the learner should
  abstain.

Cognitive load:

- Use a source spine to reduce extraneous load before asking for synthesis.
- Prefer small mini-spines for fragile distinctions, such as causal timing or
  claim-alignment alternatives.
- Add optional learner load ratings to human pilots so a higher score is not
  mistaken for a better teaching method if it is simply more exhausting.

Intelligent tutoring and knowledge tracing:

- Store claim-level evidence, not just lesson-level completion.
- Keep mastery evidence separate from benchmark evidence and draft review
  hints.
- Track the construct being tested for each item, such as direct detail,
  causal timing, confound recognition, transfer conclusion, source support, or
  fallacy cue.

## Current Didactopus Implications

The source-spine-transfer harness already supports the core pattern:

- source-blind pretest;
- condition-specific study notes;
- source-hidden, notes-only posttest;
- retention-proxy probes;
- claim-level `G` exports;
- derived study-skill artifact scoring;
- human pilot packet generation.

The next version should make the following changes explicit:

- add a causal-timing and calibration condition;
- report construct-level results so causal/timing failures are visible;
- add delayed retention runs beyond same-session retention proxies;
- add source-anchor recall items, not just true/false claims;
- add worked-example fading as a separate condition;
- add optional cognitive-load and effort ratings for human pilots;
- bootstrap confidence intervals for condition effects once there are enough
  items and runs.

## Why `G` Matters Here

Raw accuracy is too coarse for this work. The first source-spine-transfer run
showed a model with perfect retention accuracy but 0.5 confidence on every
retention item. That is not the same learning state as high-confidence,
source-grounded recall.

The practical `G` metric is useful because it can expose:

- truth tracking: whether probabilities align with correctness;
- discrimination: whether the learner separates true and false claims;
- robustness: whether performance transfers from source-near items to shifted
  items.

This can also contribute back to pedagogical and AI-tutoring research. Many AI
tutor evaluations focus on answer correctness, satisfaction, or broad learning
gain. Didactopus can add a stricter source-grounding layer: did the learner
become better calibrated about what the source actually supports?

## Experiment Roadmap

1. Run the existing source-spine-transfer experiment with the new
   `causal_timing_calibration` condition.
2. Run a delayed human self-pilot retention assessment without rereading the
   source or scoring notes.
3. Add a worked-example fading condition to separate full explanation from
   learner completion practice.
4. Add construct-level reporting for causal timing, confound recognition,
   overgeneralization, source support, and calibration.
5. Add a transfer source with the same hidden structure but different surface
   content.
6. Compare two local models across at least two sources and four conditions,
   then bootstrap condition-effect intervals.
7. Promote stable successful patterns into `mentoring-operational-process.md`
   and learner-session code.

## Citation Anchors

- Roediger and Karpicke, 2006, on test-enhanced learning and long-term
  retention: <https://doi.org/10.1111/j.1467-9280.2006.01693.x>
- Dunlosky et al., 2013, on effective learning techniques including practice
  testing and distributed practice: <https://doi.org/10.1177/1529100612453266>
- Hattie and Timperley, 2007, on feedback: <https://doi.org/10.3102/003465430298487>
- Atkinson, Derry, Renkl, and Wortham, 2000, on worked examples:
  <https://doi.org/10.3102/00346543070002181>
- Chi, Bassok, Lewis, Reimann, and Glaser, 1989, on self-explanations and
  learning from worked examples: <https://doi.org/10.1207/s15516709cog1302_1>
- Sweller, 1988, on cognitive load during problem solving:
  <https://doi.org/10.1207/s15516709cog1202_4>
- Corbett and Anderson, 1995, on knowledge tracing:
  <https://doi.org/10.1007/BF01099821>
- Nicol and Macfarlane-Dick, 2006, on formative assessment and self-regulated
  learning: <https://doi.org/10.1080/03075070600572090>
