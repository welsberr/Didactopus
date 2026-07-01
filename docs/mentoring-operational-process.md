# Mentoring Operational Process

Didactopus mentoring should be a structured learning loop over grounded
materials, not an answer service. The mentor helps the learner orient, attempt,
check evidence, revise, and accumulate demonstrated mastery.

## Inputs

A mentoring session should prefer reviewed inputs:

- concept graph and prerequisite path;
- source corpus fragments with provenance;
- reviewed reasoning scaffolds;
- Library argument records promoted through GroundRecall;
- study-aid records such as summaries, analysis notes, glossary items, worked
  examples, retrieval prompts, answer feedback, and coverage gaps;
- CiteGeist source-support records where citations matter;
- learner mastery ledger and recent weak evidence.

Draft inputs may be used only as workbench hints. They must stay visible as
draft, unreviewed, or unresolved.

For AI learners, the first input should be an initial assessment transcript that
estimates prior knowledge, uncertainty, hallucination, and calibration before
mentoring begins. Do not assume a small local model is naive; measure it.

## Session Loop

The default mentor loop is:

1. Select a concept, claim, source section, or skill from the graph and learner
   state.
2. Orient the learner with a short at-a-glance frame and the relevant source
   spine.
3. Ask for a learner attempt before giving a full answer when the goal is skill
   practice or assessment.
4. Retrieve only the source fragments, study-aid records, and scaffolds needed
   for the current step.
5. Provide a hint, worked example, or contrast case matched to the learner's
   evidence state.
6. Ask the learner to produce a public reasoning product: claim, evidence,
   uncertainty, alternative, calculation, explanation, or revision.
7. Evaluate the attempt against reviewed source records and explicit criteria.
8. Give feedback that separates source summary, mentor interpretation, and
   reviewer verdict.
9. Record mastery evidence, misconceptions, unresolved source-support gaps, and
   recommended next step.

For novices, use more worked examples and explicit structure. For stronger
learners, fade steps, ask for error-finding, require source-support checks, and
push synthesis across sources.

## Research-Grounded Practice Pattern

Mentor sessions should use a pattern consistent with retrieval practice, worked
examples, feedback, and confidence calibration research:

- orient with a source spine before asking for synthesis;
- use mini-spines for fragile distinctions such as causal timing, confounds,
  and claim-alignment alternatives;
- ask for retrieval before rereading when the goal is assessment or durable
  learning;
- use worked examples for novices, then faded examples where the learner must
  supply the missing source-support, inference, or uncertainty step;
- require confidence or uncertainty on assessed claims;
- give feedback that names the failed distinction, not just the right answer;
- add delayed retention checks when the session is meant to establish durable
  mastery.

The research rationale and experiment roadmap are summarized in
[pedagogical-research-alignment.md](pedagogical-research-alignment.md).

## Study-Aid Use

Study-aid records should be used as mentor aids, not as replacements for
sources. A mentor response may combine:

- at-a-glance orientation;
- source summary;
- analysis;
- glossary clarification;
- worked example;
- retrieval question;
- feedback or answer key.

The mentor must keep those layers distinct. It should not present analysis as
what the source says, and it should not treat an unreviewed summary as a
reviewed answer.

## Argument and Evidence Mentoring

When the lesson concerns claims, controversies, or source evaluation, the mentor
should operate on fine-grained argument records:

- proposition;
- premise;
- inference;
- conclusion;
- evidence;
- objection;
- rebuttal;
- critique;
- citation anchor;
- fallacy cue;
- claim-alignment candidate.

Fallacy cues are prompts for review and discussion, not final labels. Claim
alignment to sources such as the TalkOrigins Index to Creationist Claims should
be taught as a disambiguation task: compare candidate entries, state positive
and negative evidence, identify likely confusions, then decide or mark
unresolved.

Lineage claims should distinguish citation, quotation, paraphrase, shared
phrase, shared example, argument-order similarity, silent-borrowing candidate,
independent recurrence, and later reuse.

## Role Boundaries

`mentor`:

- orients, asks questions, gives hints, and explains feedback;
- uses reviewed scaffolds and source fragments before model prior knowledge;
- avoids completing the learner's assessed work before an attempt.

`practice`:

- generates bounded prompts, worked examples, faded examples, and retrieval
  questions;
- tags each prompt with concept, source, skill, and evidence target.

`evaluator`:

- scores demonstrated learner work against criteria;
- records evidence and uncertainty;
- is conservative when source support is missing or ambiguous.

`reviewer`:

- promotes or rejects draft study-aid records, argument records, source-support
  claims, and claim alignments.

## Guardrails

Mentoring flows must:

- preserve provenance for source-backed statements;
- label model inference, draft material, and unresolved alignment;
- refuse to promote unreviewed draft material into mastery evidence;
- avoid hidden chain-of-thought requests;
- avoid answer offloading by requiring learner attempts for assessed tasks;
- expose uncertainty when citations, claim alignment, or source support are
  incomplete;
- protect restricted Library material from learner-facing public exports.

Access-constrained mentoring adds further guardrails:

- prefer local inference, local retrieval, and local learner ledgers by default;
- avoid real-name or demographic requirements unless a deployment explicitly
  needs them;
- keep telemetry, cloud sync, crash upload, and remote model routes disabled
  unless deliberately configured;
- make remote routes and external retrieval visible before use;
- support clear export, archive, and deletion workflows for learner records;
- avoid promising secrecy, anonymity, or legal safety in hostile environments;
- keep human learner mastery evidence separate from AI learner benchmark records
  and operator maintenance logs.

The broader access-constrained roadmap is in
[access-constrained-mentoring.md](access-constrained-mentoring.md).

## Output Artifacts

Each session should be able to emit:

- `mentor_session_plan`;
- `mentor_turn`;
- `practice_prompt`;
- `worked_example`;
- `retrieval_prompt`;
- `learner_attempt`;
- `evaluator_feedback`;
- `mastery_evidence`;
- `misconception_observation`;
- `source_support_gap`;
- `claim_alignment_task`;
- `coverage_gap`;
- `next_step`.

These artifacts let Didactopus improve mentoring while keeping review,
provenance, accessibility, and local-model benchmarking attached to the same
operational backbone.

## AI Learner Benchmarks

Local LLMs can act as learner stand-ins for practice and research. The process
is defined in
[ai-learner-mentorship-benchmark.md](ai-learner-mentorship-benchmark.md).
AI-learner sessions should include source-blind pretests, source-grounded
mentorship, posttests, transfer probes, and claim-level exports for groundedness
metrics. Their evidence is benchmark evidence, not human mastery evidence.
