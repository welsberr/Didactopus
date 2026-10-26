# Lede-brief educational integration roadmap

Status: proposed, all stages pending. Prepared 2026-10-04.

Distribution remains deferred. The current public package indexes do not
provide the required Epistemap or LedeBrief releases, and the local LedeBrief
checkout has no configured remote. Keep the current Didactopus package
requirements unchanged until distributable, versioned dependencies are
available. A local adapter can then be added and tested against the published
package contract.

Use shared lede-brief packages for concise lesson introductions and complete,
navigable educational material. The [coordinating design](../../GroundRecall/docs/lede-brief-design-and-roadmap.md)
defines the formats; [Epistemap's foundation plan](../../Epistemap/docs/lede-brief-foundations-roadmap.md)
owns neutral graph operations. Links assume sibling checkouts until publication.

Didactopus retains pedagogy, learner state, review, practice and assessment
authority. Use the shared library directly; GroundRecall is optional for memory
and session integration. Reuse ConceptGraph projections and prerequisite
traversal plus existing learning promises/outcomes/activities/evidence contracts.
Do not implement another summarization engine or a divergent graph algorithm.

| Stage | Deliverable | Acceptance |
| --- | --- | --- |
| DLB-0 | Educational preservation profile and independently reviewed source/inventory fixture | Definitions, prerequisites, examples, misconceptions, explanatory reasoning and required practice are explicit; mere topic presence does not satisfy coverage. |
| DLB-1 | Adapter from reviewed source/pack data to shared lede-brief and back to a reviewable derived package | Source IDs, attribution, review status and learning objectives survive; generated packages do not silently replace approved packs or alter learner evidence. |
| DLB-2 | Prerequisite-aware reading routes and learner-appropriate explanations | Required dependencies remain available; known prerequisites may be skipped only under Didactopus policy/evidence; coverage and delivery never update mastery by themselves. |
| DLB-3 | Educational comprehension/transfer pilot and installed compatibility fixture | Compare against original instruction using learning outcomes and independent review, including needed examples, practice and feedback; shorter text alone is not success. |

DLB-0 follows LB-0/ELB-0 contracts. DLB-1 uses shared LB-1 through LB-3 as needed;
DLB-2 consumes tested ELB-1/ELB-2 operations; DLB-3 contributes to LB-5/ELB-3.
Offline fixtures need no GroundRecall deployment or session registry. Existing
UPR-0 restrictions remain when connecting unified retrieval.

Preserve the priorities and correctness gates in the
[educational graph roadmap](educational-graph-correction-roadmap.md) and
[process improvement roadmap](process-improvement-roadmap.md). This proposal
does not change the October demonstration scope. Honor provider dispatch and
independent evaluation requirements when model-backed generation is introduced.

Keep learner responses, assessment answers and private mastery data out of
public briefs. A faithful complete account may still be poor instruction;
pedagogical acceptance must be evaluated separately. Missing prerequisites,
removed counterexamples, confusingly compressed reasoning and source revisions
are required regression cases.
