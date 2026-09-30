# Didactopus: graph correctness and educational alignment roadmap

Status: implementation in progress. Prepared 2026-09-30 with OpenAI Codex
assistance for Wesley R. Elsberry. Demo target: 2026-10-23.

## Purpose and relationship to other plans

Make graph diagnostics safe to interpret, then connect existing educational
contracts to evidence of what learners can do and explain. Reuse Epistemap for
neutral algorithms and preserve Didactopus's responsibility for pedagogy.

The coordinating [Epistemap roadmap](https://github.com/welsberr/Epistemap/blob/main/docs/educational-graph-correction-roadmap.md)
defines packages EG-0–EG-5. Before publication, the sibling checkout contains it
at `../Epistemap/docs/educational-graph-correction-roadmap.md` from this repository
root. This plan complements the existing mentor-loop and pedagogy roadmap; it does
not replace them with a software-porting product. Avida-ED supplies a bounded
worked example, not the definition of all Didactopus learning tasks.

The separate unified-retrieval companion plan remains blocked on GroundRecall
UPR-0 as documented there. Standalone graph repairs and offline learning-pack
checks do not require that new integration. Do not register learner responses,
private ledgers, or assessment answers as general retrieval corpora.

## What the current code establishes

Baseline: `f0b0e8ac55459e05bdf16604ec971ea266278b84`.

- **Confirmed misleading result:** `graph_qa_for_pack()` returns zero warnings
  when required files are absent. An empty-directory probe reproduced this.
  Callers receive no explicit indication that analysis did not run.
- **Confirmed metric/description mismatch:** the “bottleneck” check uses direct
  out-degree with threshold three, not the total number of downstream dependents.
  It is a heuristic flag, not an established educational bottleneck.
- **Source-level limitations to cover with regression tests:** graph QA calls the
  loader rather than full structural validation; duplicate IDs and invalid
  prerequisite references need explicit treatment. Raw edge counts and set-based
  adjacency can disagree on repeated prerequisites. Recursive traversal needs a
  deep-chain case. Longest-path output is not a valid full-DAG metric on a cycle.
- **Reuse already exists:** `ConceptGraph` projects to Epistemap and uses filtered
  prerequisite traversal. The `pedagogy` module already supplies learning promises,
  observable outcomes, activities, evidence and author-review foundations. Do not
  specify these as if they must be invented from scratch.
- **Documentation drift:** the main roadmap lists some pedagogical contract work
  as both implemented and remaining. Resolve this against code and tests, without
  treating implemented foundations as completed learner-pilot validation.

The first two findings have high confidence from runtime/source inspection.
Additional malformed-pack and scale cases are audit targets, not claims that all
have already failed in deployed workflows. The separate Epistemap cycle-membership
defect was also reproduced; its correction precedes the dependency-pin update.

## DG-1 — make invalid input explicit (October 1–4)

Dependency: EG-0's contract agreement; independent of the Epistemap fix.

Separate file loading, shape validation, graph integrity, and educational QA.
Validate YAML root/container types before accessing mappings or iterating concept
objects. Report absent files, parse failures, wrong types, missing/duplicate IDs,
unknown prerequisite endpoints, and invalid prerequisite lists as structured
errors. Decide explicitly whether repeated prerequisite entries are errors or
normalized with a warning; preserve source locators either way.

Return an additive versioned result distinguishing invalid input, analysis not
run, completed analysis, advisory findings, and metrics. Do not represent a metric
that could not be computed as a reassuring zero. Preserve legacy warning fields
for readers during migration, but update acceptance callers to inspect status.
Do not change learner evidence or mastery as a side effect of validation.

Acceptance: missing, malformed, scalar/list-root, duplicate-ID, dangling-edge,
empty-valid, and ordinary-valid fixtures have explicit expected outcomes. All
discovered consumers distinguish “not analyzed” from “analyzed with no findings.”
Where a CLI or job exposes acceptance, invalid input causes a failing result;
verify the actual caller before claiming a gate exists.

## DG-2 — explain structural metrics accurately (October 4–7)

Dependencies: DG-1; EG-1/EG-3 before using the corrected Epistemap release.

Use shared filtered graph operations where they fit instead of maintaining a
second divergent cycle detector. Define the prerequisite direction as prerequisite
→ dependent concept. Distinguish direct dependents, unique reachable dependents,
cyclic components, nodes blocked by those components, and isolated concepts.
Compute DAG depth only on an acyclic view; otherwise report it unavailable or
explicitly scoped to a condensation graph, with a different metric name.

Replace unsupported “bottleneck” certainty with “high direct dependency count”
or another accurate advisory description. Make thresholds configurable by a
versioned profile; record defaults and the profile used. Sparse graphs, isolated
introductory concepts, and long chains can be intentional. Findings should carry
IDs, affected concepts, evidence, rationale, severity, and a review disposition:
accept concern / intentional design / false positive / needs evidence.

Acceptance: direct versus transitive count fixtures differ correctly; valid
interaction/related-to loops do not trigger prerequisite errors; cycle-with-tail
membership is correct; results are deterministic under reordered input. Review
the existing `tests/test_graph_qa.py` expectations rather than preserving misleading
wording solely to satisfy them. Pin and test the released Epistemap correction.

## DG-3 — connect objectives, tasks, and assessment (October 7–10)

Dependencies: DG-1; reuse existing pedagogy contracts immediately.

Create a small mutation-and-variation learning pack with concept prerequisites,
observable outcomes, learner predictions, observations, explanations, and a
reviewable rubric. Map those to existing `pedagogy` fields; identify any missing
fields before proposing extensions. Preserve stable IDs and source attribution.

Ask whether each selected objective has an activity that elicits it, evidence
that could support it, and assessment criteria that distinguish common
misconceptions. Check prerequisites at the point of use. Treat a missing linkage
as a coverage finding; a present linkage does not prove the activity is effective.

For the demonstration, distinguish sequence richness from mutation count,
ancestry, or adaptation; updates from generations; and observed replicate
variation from universal conclusions. Avida-ED remains responsible for verifying
engine and metric semantics. Didactopus structures the questions and review.

Acceptance: removing an explanation prompt exposes an unassessed objective;
restoring it resolves that structural finding without incrementing mastery.
An instructor can inspect the source, rationale, and rubric. Qualified educational
review is pending until a reviewer actually records it.

## DG-4 — bounded porting adapter and readable report (October 10–15)

Dependencies: DG-2, DG-3, EG-3.

Project only the educational subgraph into Didactopus. Keep application workflow
states, controls, scientific metrics, code references, test definitions, and
test executions in the Avida-ED adapter. Use the existing Epistemap models and
namespaced relation types; retain provenance, review status, and assessment
dimensions through round trips.

Join the views to answer five bounded questions: missing implementation/current
verification; missing assessment opportunity; missing scientific definition;
stale evidence; and candidate change impact. Return witness paths or missing
obligations in a concise report. Do not present reachability as proof of actual
impact. Keep accepted, intentionally different, unknown, and failed states distinct.

Acceptance: one real omission has a source, disposition, corrective action, and
rerun. Include labeled negative fixtures for absent edges and stale build evidence.
The adapter must not expose private learner text or turn a passing software test
into learner evidence. A plain report is sufficient; a graph visualization is optional.

## DG-5 — review and demo readiness (October 16–23)

Dependencies: DG-4 and EG-5 release checks.

Validate installed dependencies, the bounded pack, and report generation on the
presentation machine. Review rendered output and keyboard/readability behavior.
Keep Spanish activity text and terminology separate from scientific identifiers;
human language and visual review remain explicit acceptance steps where used.

Freeze the candidate October 20. Archive fixtures, source/pack hashes, diagnostic
profiles, dependency versions, review records, and an offline replay. Demonstrate
an analysis failure being correctly rejected and a genuine improvement being
verified. Explain which result came from Didactopus, Epistemap, the app adapter,
or human judgment.

If time is short, retain DG-1/DG-2, a small reviewed pack, and a static traceability
report. Defer a generalized query engine, learner UI redesign, and new retrieval
integration. Do not advertise unsupported learning or productivity benefits.

## Work after the demonstration

1. **Integrate the learning contract into the standard session flow.** Render why
   an activity matters, what to notice, what to do, and how evidence will be
   reviewed. Preserve predictions and explanations; offer hints and retrieval
   practice without defaulting to answer replacement.
2. **Support author review and source changes.** Stable findings and source IDs,
   merge/split decisions, reviewed aliases, explicit invalidation, and graph diffs
   should preserve history without carrying obsolete acceptance forward. Keep
   private learner records separate from public pack changes.
3. **Validate educational usefulness.** Evaluate authoring time, actionable
   findings, false alarms, and review burden first. Separately assess learners'
   understanding, transfer, retention, calibration, access, and workload under
   an appropriate study design. AI-learner benchmarks are not human learning evidence.
4. **Extend to additional curricula and porting tasks.** Use a second real example
   to decide which adapter features generalize. Do not make Avida-specific settings
   part of the generic learning model.
5. **Reconcile documentation with implementation.** Remove duplicated completed
   items from “remaining work,” retain explicit pilot/integration gaps, and make
   each status refer to evidence at a named revision. Coordinate with the existing
   uncommitted roadmap work rather than overwriting it.

## Progress, responsibility, and evidence

### Recorded implementation update — 2026-09-30

- **DG-1: implemented locally, suite verified.** YAML roots and list entries now
  require expected structures; malformed rows, non-string prerequisite lists,
  and dangling prerequisite IDs produce invalid-input errors. Invalid packs
  return `status: invalid_input`, `analysis_status: not_run`, and a null warning
  count rather than a false zero-warning result.
- **DG-2: implemented locally, suite verified.** Cycle members are grouped using
  strongly connected components; acyclic descendants are listed separately.
  High direct dependency count is named accurately. Repeated prerequisites do
  not inflate the edge count. Longest chain is unavailable for cyclic graphs
  rather than reporting an incomplete value. Heuristics remain advisory and are
  not pedagogically validated.
- **Dependency update:** Didactopus now pins Epistemap `v0.1.0a5`; the new
  Didactopus package version is `0.1.2`.
- **DG-3, DG-4, DG-5: planned.** Existing pedagogy facilities have not yet been
  audited into the Avida pack, connected to porting assertions, or reviewed by
  an instructor for this integration.

Verification on 2026-09-30: full Didactopus suite `312 passed`; full Epistemap
suite `173 passed`; GroundRecall full suite `534 passed`; CiteGeist full suite
`315 passed, 5 skipped`. Consumer suites used the modified Epistemap source tree,
not a newly published package. GroundRecall's six local HTTP tests passed only
in an unsandboxed rerun. This does not establish package deployment, learner
outcomes, or tutorial equivalence.

Assign implementation and review owners before future packages. Wesley R.
Elsberry is the proposed project steward, not an assumed signatory for reviews
that have not occurred.

For each package maintain: status, owner, UTC update, dependency revisions,
changed paths, reproducer/tests, actual result, evidence links, reviewer decision,
remaining limitations, and next action. Record hours prospectively if assessing
effort. The date windows are planning targets, not estimates of measured savings.

Source inspection covered `graph_qa.py`, `pack_validator.py`, `concept_graph.py`,
graph QA tests, and current roadmap/pedagogy descriptions on 2026-09-30. The local
empty-pack probe reproduced the false-clean diagnostic shape. Runtime corrections
are implemented in the local checkout; the Avida integration and learner pilots
remain pending.
