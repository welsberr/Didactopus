# Didactopus

Didactopus is an AI-assisted learning and knowledge-graph platform for representing
how understanding develops, how concepts relate, and how learner output can be
reused to improve packs, curricula, and downstream agent skills.

It is designed for:

- human learners
- AI learners
- human/AI collaborative learning workflows
- curriculum designers
- mentors and reviewers
- researchers studying learning trajectories

The system treats learning as a graph process rather than as a sequence of isolated
quiz events. Domain packs define concepts, prerequisites, and cross-pack
relationships. Learner evidence updates mastery estimates and produces reusable
artifacts.

## Major capabilities

### Domain packs
Domain packs define concept graphs, prerequisite relationships, and optional
cross-pack links. Packs may be private, shared, reviewed, or published.

### Learner state
Learners accumulate evidence events, mastery records, evaluation outcomes, and
trajectory histories.

### Animated graph views
Learning progress can be rendered as stable animated concept graphs and exported
as frame bundles for GIF/MP4 production.

### Artifact registry
Render bundles, knowledge exports, and derivative outputs are managed as
first-class artifacts with retention metadata and lifecycle controls.

### Knowledge export
Learner output can be exported as candidate structured knowledge, including:

- pack-improvement suggestions
- curriculum draft material
- skill-bundle candidates
- archived observations and discovery notes

### Review and promotion workflow
Learner-derived knowledge is not treated as automatically correct. It enters a
triage and review pipeline where it may be promoted into accepted Didactopus
assets.

### Synthesis engine
Didactopus emphasizes synthesis: discovering helpful overlaps and structural
analogies between distinct topics. The synthesis engine proposes candidate links,
analogy clusters, and cross-pack insights.

---

## Philosophy

### Learning as visible structure
The system should make it possible to inspect not just outcomes, but how those
outcomes emerge.

### Learners as discoverers
Learners sometimes find gaps, hidden prerequisites, better examples, or novel
connections that mentors did not anticipate. Didactopus is designed to capture
that productively.

### Synthesis matters
Some of the most valuable understanding comes from linking apparently disparate
topics. Didactopus explicitly supports this through:

- cross-pack links
- similarity scoring
- synthesis proposals
- reusable exports for pack revision and curriculum design

### Reuse beyond Didactopus
Learner knowledge should be renderable into forms useful for:

- improved domain packs
- traditional curriculum products
- agentic AI skills
- mentor notes
- research artifacts

---

## New additions in this update

This update adds design material for:

- review-and-promotion workflow for learner-derived knowledge
- synthesis engine architecture
- updated README and FAQ language reflecting synthesis and knowledge reuse

See:

- `docs/review_and_promotion_workflow.md`
- `docs/synthesis_engine_architecture.md`
- `docs/api_outline.md`
- `docs/data_models.md`
- `FAQ.md`
