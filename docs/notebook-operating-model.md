# Notebook Operating Model

This note records what the Foundation Notebook pilot changed about how
Didactopus should be understood.

The main conclusion is that the Notebook is not just another output format. It
is the durable knowledge layer between raw source-grounding work and
learner-facing products.

Didactopus should therefore operate with three layers:

1. source-grounded substrate
2. Notebook knowledge layer
3. learner-facing and workbench-facing products derived from that layer

## 1. Source-grounded substrate

This is the ingestion and review layer:

- `doclift`
- Wolfe-guided source discovery and local-corpus selection
- `GroundRecall`
- `CiteGeist`

Its job is not only to collect sources, but to preserve enough structure to
support later explanation, review, and public accountability.

The pilot showed that this layer needs more than raw topic labels and extracted
claims. It needs to preserve:

- source role
- concept neighborhood hints
- terminology
- scope conditions
- contrasts
- quote candidates
- bibliographic support

## 2. Notebook knowledge layer

The Notebook is the durable concept-network representation.

It should be treated as primary for knowledge organization, but supplemental
relative to the final learner workflow. Learners do not necessarily consume the
Notebook directly as their main experience, but Didactopus should derive its
best learner products from it.

The pilot showed that the Notebook should be:

- hub-first rather than topic-label-first
- neighborhood-oriented rather than article-oriented
- distinction-aware rather than summary-only
- source-grounded but normally paraphrastic in public rendering

The broadest useful hub in the pilot was not a narrow topic like
`population biology`, but a broader explanatory center such as
`Evolutionary Dynamics of Populations`.

That shift matters. The Notebook should preserve explanatory structure such as:

- populations and variation
- inheritance and mutation
- selection and drift
- adaptation and accommodation
- organism-environment interaction
- common descent and divergence

## 3. Derived products

Didactopus should derive multiple product types from the same Notebook layer:

- learner workbench views
- guided lessons and learning paths
- mentor/practice/evaluator session grounding
- review workbench artifacts
- public Notebook pages
- argumentation/workbench bundles

These products should not collapse into one another.

Different renderings need different rules:

- Notebook rendering:
  preserve concept structure, source trails, and review context
- Workbench rendering:
  surface definitions, caveats, distinctions, and quote candidates
- Public exposition:
  stay paraphrastic by default, mark all quotations, and show source citation

## Required extraction classes

The pilot made it clear that Didactopus needs more than “claim extraction”.

The durable extraction classes should include:

- explanatory claims
- definitions
- qualifications
- constraints
- contrasts and distinctions
- quote candidates
- source-trail and bibliographic support
- learner-significance cues

The distinction layer is especially important for learning. Many concepts are
best learned not as isolated statements but as structured contrasts:

- `A vs B`
- `A does not imply B`
- `B can occur without A`
- `A is one mechanism among several`

For the evolution pilot, this includes distinctions such as:

- selection versus drift
- adaptation versus accommodation
- heredity versus epigenetic inheritance
- short-term response versus long-run evolutionary change

## Source-role weighting

The pilot also showed that not all sources do the same work.

Didactopus should preserve source-role weighting so later products can choose
better supporting material for the task at hand.

At minimum, sources should be classifiable as:

- overview
- mechanism
- nuance
- controversy
- argumentation

Short web captures were often good enough for overview and argumentation.
Wolfe-selected local textbook material was substantially better for nuance,
qualification, and constraint extraction.

That means source selection should not be treated as neutral. The system should
prefer different source roles for different downstream tasks.

## Secondary products are not accidental

Definitions, constraints, qualifications, and quote candidates should be
treated as first-class secondary products, not as incidental by-products of
review.

These secondary products matter because they support:

- explanation quality
- misconception prevention
- learner revision
- source-grounded argumentation workflows
- public accountability

The pilot showed that a strong Notebook/workbench flow depends heavily on these
secondary lanes.

## Citation and quotation policy

The public-facing rule is simple:

- quotes must stay marked and attributed
- public prose should normally be paraphrastic
- unmarked source wording is not acceptable in public Notebook exposition

This should remain explicit in both workbench and publication paths.

## Operational implications

Near-term Didactopus work should therefore prioritize:

1. Notebook-centered concept organization
2. first-class distinction modeling
3. source-role-aware retrieval and ranking
4. first-class secondary products
5. separate rendering contracts for Notebook, workbench, and public exposition

The notebook is not the only Didactopus output. It is the durable center that
lets the other outputs stay grounded, explainable, and pedagogically useful.

For the implementation sequence that follows from this model, see
[notebook-implementation-plan.md](./notebook-implementation-plan.md).
