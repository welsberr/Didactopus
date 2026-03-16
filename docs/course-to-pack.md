# Course-to-Pack Pipeline

The course-to-pack pipeline turns source material into a Didactopus draft domain pack.

## Current code path

The main building blocks are:

- `didactopus.document_adapters`
  Normalize source files into `NormalizedDocument`.
- `didactopus.topic_ingest` and `didactopus.course_ingest`
  Build `NormalizedCourse` data and extract concept candidates.
- `didactopus.rule_policy`
  Apply deterministic cleanup and heuristic rules.
- `didactopus.pack_emitter`
  Emit pack files and review/conflict artifacts.

## Supported source types

The repository currently accepts:

- Markdown
- plain text
- HTML
- PDF-ish text
- DOCX-ish text
- PPTX-ish text

Binary-format adapters are interface-stable but still intentionally simple.

## Intermediate structures

The ingestion path works through these data shapes:

- `NormalizedDocument`
- `NormalizedCourse`
- `TopicBundle`
- `ConceptCandidate`
- `DraftPack`

## Current emitted artifacts

The pack emitter writes:

- `pack.yaml`
- `concepts.yaml`
- `roadmap.yaml`
- `projects.yaml`
- `rubrics.yaml`
- `review_report.md`
- `conflict_report.md`
- `license_attribution.json`
- `source_corpus.json`

`source_corpus.json` is the main grounded-text artifact. It preserves lesson bodies, objectives,
exercises, and source references from the ingested material so downstream tutoring or evaluation
can rely on source-derived text instead of only the distilled concept graph.

## Rule layer

The current default rules:

- infer prerequisites from content order
- merge duplicate concept candidates by title
- flag modules that look project-like
- flag modules or concepts with weak extracted assessment signals

These rules are intentionally small and deterministic. They are meant to be easy to inspect and patch.

## Known limitations

- title-cased phrases can still become noisy concept candidates
- extracted mastery signals remain weak for many source styles
- project extraction is conservative
- document parsing for PDF/DOCX/PPTX is still lightweight

## Reference demo

The end-to-end reference flow in this repository is:

```bash
python -m didactopus.ocw_information_entropy_demo
```

That command ingests the MIT OCW Information and Entropy source file or directory tree in `examples/ocw-information-entropy/`, emits a draft pack into `domain-packs/mit-ocw-information-entropy/`, writes a grounded `source_corpus.json`, runs a deterministic agentic learner over the generated path, and writes downstream skill/visualization artifacts.
