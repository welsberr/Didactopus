# Notebook Implementation Plan

This note turns the Notebook operating model into a concrete Didactopus
implementation sequence.

It assumes the conclusions in
[notebook-operating-model.md](./notebook-operating-model.md):

- the Notebook is the durable knowledge layer
- learner products should derive from it
- distinctions, qualifications, constraints, and source roles are first-class
- public rendering must stay source-grounded and paraphrastic by default

## Goal

Make Didactopus operate as a system with:

1. source-grounded ingestion and review
2. a durable Notebook concept network
3. learner, workbench, and public products derived from that network

The key implementation mistake to avoid is treating the Notebook as a static
page generator. It should instead be the stable intermediate representation
that other Didactopus products depend on.

## Phase 1. Strengthen the source-grounded substrate

Primary concern:

- preserve the information needed to build a useful Notebook later

Required additions at this layer:

- source role classification:
  - overview
  - mechanism
  - nuance
  - controversy
  - argumentation
- distinction candidates:
  - `A vs B`
  - `A does not imply B`
  - `B can occur without A`
- learner-significance cues:
  - why this distinction matters
  - what misconception it prevents
  - what explanatory work it does
- first-class secondary products:
  - definitions
  - qualifications
  - constraints
  - quote candidates

Expected implementation targets:

- `GroundRecall` review/export payloads
- `CiteGeist` bibliography support and claim-support outputs
- source-adapter metadata from `doclift` and related import flows

Completion indicators:

- concept review payloads expose source roles
- distinction-like claims are tagged explicitly
- secondary products are inspectable without custom post-processing

## Phase 2. Build Notebook-native concept structure

Primary concern:

- organize knowledge around explanatory hubs rather than narrow labels

Required additions:

- explicit hub-concept representation
- first-ring and second-ring neighborhood representation
- support for concept aliases without collapsing meaningful distinctions
- preferred-source selection by source role
- Notebook-level summaries built from grounded claims plus secondary products

Expected Didactopus targets:

- `notebook_page` payload shape
- hub/neighborhood builder logic
- pack emission for Notebook-facing artifacts

Completion indicators:

- a Notebook page can identify:
  - the primary hub
  - first-ring neighbors
  - key distinctions
  - preferred overview/mechanism/nuance sources
- bibliography topics no longer have to serve as the primary Notebook center

## Phase 3. Make distinctions learner-facing

Primary concern:

- learning works better when concepts are contrasted, qualified, and scoped

Required derived-product features:

- distinction panels in learner workbench views
- definitions, constraints, and qualifications surfaced beside explanations
- “why this matters” cues for important conceptual differences
- quote/source-trail views for argumentation workflows

Expected Didactopus targets:

- learner workbench UI and backend payloads
- mentor/practice/evaluator session grounding
- lesson and activity generation

Completion indicators:

- learner-facing explanations can say not only what something is, but also:
  - what it is not
  - what it does not imply
  - what nearby concepts it is often confused with
- practice prompts can target misconceptions and contrastive understanding

## Phase 4. Separate rendering contracts

Primary concern:

- the same Notebook knowledge should support different output modes without
  blurring their rules

Three rendering contracts should be explicit:

### Notebook contract

- preserve concept structure
- preserve source trails
- preserve review context
- preserve distinctions and caveats

### Workbench contract

- surface definitions, constraints, qualifications, and quote candidates
- prefer inspectability over polish
- retain enough detail for argumentation and source checking

### Public exposition contract

- prefer paraphrase over copied wording
- mark all quotations explicitly
- attach source citation in display
- never present unmarked source wording as original Didactopus prose

Expected Didactopus targets:

- notebook-page rendering
- workbench payloads and views
- public publication/export paths

Completion indicators:

- public pages can be audited for quote marking and citation display
- workbench pages expose more raw source-oriented structure than public pages

## Phase 5. Source-role-aware retrieval and ranking

Primary concern:

- different tasks need different kinds of support

Retrieval should be able to prefer:

- overview sources for first-pass orientation
- mechanism sources for explanatory detail
- nuance sources for qualifications and constraints
- controversy sources for dispute framing
- argumentation sources for rebuttal and debate workflows

This should influence:

- Notebook page support lists
- learner-session grounding
- workbench recommendation ordering
- quote-candidate selection

Completion indicators:

- the same concept can yield different ranked source sets for
  `learn`, `review`, `argue`, and `publish` contexts

## Phase 6. Pack and publication alignment

Primary concern:

- the Notebook must become a stable export surface for other Didactopus flows

Needed outputs:

- Notebook-aware pack format additions
- workbench-friendly secondary-product exports
- publication-safe Notebook/public page export rules

Expected Didactopus targets:

- pack emission
- backend API payloads
- public export and frontend consumption

Completion indicators:

- packs can carry hub concepts, neighborhood structure, secondary products, and
  source-role metadata
- public and workbench consumers can rely on one shared substrate while
  rendering differently

## Near-term priority sequence

The next practical Didactopus sequence should be:

1. make distinctions first-class in review/export payloads
2. add source-role metadata to Notebook-facing outputs
3. upgrade `notebook_page` to summarize hub, neighborhood, and secondary lanes
4. expose secondary-product and distinction views in learner/workbench flows
5. enforce explicit public citation and quote-marking contracts
6. keep a `.groundrecall/work-map` in active projects so source roots,
   temporary builds, exports, and deployment targets remain easy to locate

## Related modernization tasks

The Notebook work now clearly depends on adjacent modernization tasks:

- expand bibliography keyword/keyphrase coverage so CiteGeist and TOA
  bibliography support reflect Notebook terminology
- harvest terminology from book indexes as a separate authoritative signal
- ingest opposition-index terminology as a salience signal with lower authority
  weight
- attach citation-block fallbacks to pages that are not yet citation-complete
- schedule citation expansion for pages that already have some citations
- keep a timeline framework in scope for rollout even if the fuller timeline
  graph is a later phase

## What the pilot changed

Before the pilot, it was reasonable to think of the Notebook as a side product
assembled from reviewed concepts.

After the pilot, the stronger view is:

- the Notebook should be the stable center of Didactopus knowledge organization
- learner products are better when built from Notebook structure
- short web captures and longer textbook sources should play different roles
- definitions, qualifications, constraints, and quotes are not optional extras

That change should guide both schema evolution and product decisions.
