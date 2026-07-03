# evo-edu Notebook Pipeline

This note turns the current `Notebook` idea into a concrete cross-repo
workflow for `doclift`, `GroundRecall`, `Didactopus`, and `CiteGeist`.

The target is the conceptual resource at:

- <https://evo-edu.org/evo/notebook/>

The important shift is that the Notebook should not be treated as "just another
wiki". The strongest differentiator available in the current stack is
graph-first navigation over reviewed concepts, claims, citations, and learner
next-step suggestions.

## Why this fits the current stack

The stack already divides responsibility in a useful way:

- `doclift`: normalize messy source material into deterministic bundles
- `GroundRecall`: canonical reviewed claims, concept graph, provenance, and
  query/export surfaces
- `Didactopus`: learner-facing packs, sequencing, workbench flows, and concept
  navigation
- `CiteGeist`: bibliography extraction, enrichment, review, and expansion

The Notebook use case needs all four:

- explanation text
- accessible concept sequencing
- explicit source grounding
- bibliography compilation and enrichment
- illustration planning
- visible graph structure for "what to learn next"

## Source classes

The Notebook will likely need at least four source classes.

### 1. Web corpora

Examples:

- TalkOrigins Archive FAQs and articles
- TalkDesign posts
- Panda's Thumb posts

Operational note:

- these corpora should be provisioned locally before ingestion
- do not rely on live scraping as the primary production path
- keep source snapshots versioned or at least manifest-tracked

### 2. Scanned textbooks and monographs

Examples already named:

- Futuyma, `Evolutionary Biology`
- Pianka, `Evolutionary Ecology`
- Bowler, `Evolution: The History of an Idea`

The current local library root is:

- `/mnt/CIFS/pengolodh/Docs/Library`

This should be treated as the upstream source corpus, not as the final working
directory for Notebook artifacts.

### 3. Bibliographic seed corpora

Examples:

- TalkOrigins bibliographies
- textbook reference sections
- existing `.bib` files in the library

These are where `CiteGeist` becomes especially important.

### 4. Planned illustration sources

These are not just assets. They should be reviewable planning objects:

- target concept
- illustration intent
- source basis
- rights/compliance note
- status: planned / needed / drafted / reviewed / published

## Recommended working position for the Notebook

The Notebook should be positioned as:

- a graph-guided conceptual atlas
- a source-grounded explanation layer
- a learner-facing bridge between articles, textbooks, and bibliographies

It should not try to compete by being the flattest or largest encyclopedia.

The distinguishing feature should be that the learner can see:

- antecedent concepts
- nearby or "closer" concepts
- derivative or downstream concepts
- representative supporting sources
- bibliography growth points
- illustration opportunities

That is much more consistent with the current stack than a generic article CMS.

## Proposed pipeline

### Phase 0. Provision the corpora locally

Create a local Notebook source workspace containing:

- provisioned web corpora snapshots
- selected textbook scan directories
- bibliography seeds
- source manifests

Expected result:

- stable local inputs for repeatable ingestion

### Phase 1. Normalize source material with `doclift`

Use `doclift` for:

- OCR-derived text normalization where practical
- sidecar generation
- `document.chunks.json` emission
- bundle manifests for scanned or converted materials

For web corpora, either:

- convert into bundle-like normalized document trees, or
- ingest through direct text/markdown adapters where that is simpler

Expected result:

- deterministic source bundles for longer-form documents

### Phase 2. Build bibliographic substrate with `CiteGeist`

Use `CiteGeist` to:

- scrape or ingest TalkOrigins bibliography materials
- expand weak references
- enrich textbook references
- cluster duplicates
- build review exports for uncertain entries
- maintain one or more Notebook `.bib` outputs

Expected result:

- a reviewed bibliography layer rather than ad hoc citation lists

### Phase 3. Import canonical knowledge into `GroundRecall`

Use `GroundRecall` to import:

- `doclift` bundles for textbooks and scans
- provisioned article/essay corpora
- optional Didactopus-native artifacts where useful

Then use its review flow to:

- standardize concepts
- preserve fragments and provenance
- compute graph diagnostics
- queue bridge/isolated/small-component concepts for review
- retain review rationale in promoted candidates

Expected result:

- canonical Notebook concept/claim substrate with provenance and graph signals

### Phase 4. Export pack-ready concept bundles from `GroundRecall`

For important notebook concepts, export:

- `groundrecall_query_bundle.json`
- `graph_interchange.json` when a graph-aware workbench needs broader
  neighborhood and quality diagnostics

If you only need the page-ready artifact for a concept, `Didactopus` now also
has a direct wrapper that writes both the query bundle and `notebook_page.json`
into one output directory:

```bash
didactopus notebook-page-groundrecall \
  /path/to/groundrecall-store \
  natural-selection \
  /tmp/notebook-page-export
```

This becomes the handoff object for learner-facing or page-facing pack flows.

Expected result:

- reviewed concept payloads that can feed Didactopus and page generation

### Phase 5. Build `Didactopus` packs and learner navigation

Use `Didactopus` to:

- create draft packs around concept neighborhoods or topical modules
- carry `groundrecall_query_bundle.json` as a declared supporting artifact
- consume `graph_interchange.json` for graph quality and neighborhood context
- expose learner-workbench context that includes review and graph signals
- sequence "what next" items from prerequisites and nearby graph structure

Expected result:

- learner-facing concept packs grounded in reviewed Notebook knowledge

### Phase 6. Publish the Notebook

Publication outputs should probably include:

- accessible concept pages
- graph-first navigation controls
- bibliography sections or per-page reading lists
- illustration status or image slots
- links into interactive apps and learner-workbench flows

Expected result:

- a Notebook that is not just readable, but navigable through conceptual
  structure

## Knowledge-graph-first navigation

This is the main product differentiator.

For each concept page, the learner should be able to see a small graph-guided
navigation panel with categories such as:

- `Antecedent concepts`
  Concepts that must usually be understood first

- `Closer concepts`
  Nearby concepts in the same explanatory neighborhood

- `Derivative concepts`
  Concepts that extend or depend on the current concept

- `Supporting sources`
  Canonical bibliography or source entries that materially support the concept

- `Illustration opportunities`
  Candidate figures or planned visual explanations

The labels can be refined later, but the structure should come from typed graph
relations rather than from arbitrary page links alone.

## Suggested relation types for Notebook navigation

The current stack does not need all of these on day one, but they are useful as
target categories:

- `prerequisite`
- `supports`
- `contrasts_with`
- `historical_predecessor`
- `historical_successor`
- `applies_to`
- `example_of`
- `misconception_about`
- `illustrated_by`

Some can live in `GroundRecall` first and only later appear in learner-facing
Didactopus packs.

## Illustration planning

Illustrations should be tracked as structured planning artifacts, not buried in
page notes.

At minimum, each planned illustration should record:

- target concept id
- working caption or purpose
- source grounding
- rights/compliance note
- priority
- status

This can begin as JSON or markdown sidecars before becoming a richer model.

## Bibliography strategy

The Notebook may want both:

- per-concept reading lists
- larger topical bibliographies

Recommended split:

- `CiteGeist` maintains the main bibliography workbench and review discipline
- `GroundRecall` stores links between concepts/claims and source artifacts
- published Notebook pages surface only the citations relevant to the current
  concept and nearby graph region

That avoids turning the Notebook itself into the bibliography editor.

## Concrete first pilot

A good first Notebook pilot would be one narrow concept region rather than the
whole corpus.

For example:

- historical development of evolutionary thought
- evidence for common descent
- natural selection and adaptation

Choose one region with:

- 1 to 3 textbooks
- a small local article/blog corpus
- one reviewed bibliography export
- one explicit graph-navigation experiment

## Recommended next implementation tasks

1. Provision one local Notebook corpus workspace outside the library root.
2. Choose one pilot concept region and one target concept.
3. Normalize one textbook source with `doclift`.
4. Provision one local TalkOrigins or Panda's Thumb snapshot.
5. Run `CiteGeist` on the pilot bibliography inputs.
6. Import the pilot sources into `GroundRecall`.
7. Export one `groundrecall_query_bundle.json`.
8. Feed that into a `Didactopus` pack flow.
9. Prototype one Notebook page that exposes graph-guided next-to-learn links.

## Bottom line

The Notebook is a strong fit for the current stack if it is treated as:

- concept-first
- graph-guided
- provenance-aware
- bibliography-backed
- learner-navigable

It is a weaker fit if treated as only a flat wiki rewrite of source material.
