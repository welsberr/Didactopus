# Library Argument Ingestion

Didactopus should use reviewed Library argument records to build learning
materials without flattening controversies into unsupported summaries.

## Inputs

Preferred inputs are GroundRecall-promoted records with:

- reviewed propositions and premises;
- explicit evidence and citation anchors;
- objections and rebuttals;
- misconception or fallacy cues;
- access/publication status;
- source provenance.

Raw doclift chunks and LLM outputs may be used only as draft material for pack
construction queues.

## Learning Outputs

Argument records can support:

- misconception maps;
- worked critique exercises;
- fallacy-recognition exercises with false-positive discussion;
- evidence evaluation prompts;
- prerequisite concept graphs;
- claim-support practice;
- source-comparison activities;
- public controversy timelines.

Each generated activity should retain source links back to reviewed records and
should distinguish what the source says from what the curriculum asks the
learner to infer.

## Study-Aid Pack Pattern

Didactopus packs can borrow the useful structure of durable study aids:

- at-a-glance orientation for the source, topic, or claim family;
- section-by-section source summaries;
- explicit analysis separated from summary;
- glossary and concept cards;
- worked examples showing how evidence or critique is evaluated;
- faded examples that remove steps as learner expertise increases;
- short retrieval-practice quizzes with feedback;
- essay or project prompts for synthesis;
- coverage status and unresolved questions.

For technical, citation, or argument-analysis skills, worked examples should
show the problem statement, source evidence, intermediate reasoning steps, final
judgment, and why tempting alternatives are wrong. For advanced learners, the
pack should shift toward partial examples, error-finding, and independent
source-support checks.

## Ensemble-Complete Ingestion

Long files and multi-file source sets should be ingested with a non-interactive
ensemble pass before review or promotion. The pass must scan every supported
source, write checkpoints, emit draft claims, concepts, observations,
fragments, and review candidates, and continue when an extracted item is
ambiguous. A claim or concept candidate is never a stop condition.

Use:

```sh
didactopus ingest-ensemble /path/to/source-tree --out-dir /path/to/run --checkpoint-every chunk
```

The command writes `manifest.json`, `sources.jsonl`, `fragments.jsonl`,
`observations.jsonl`, `claims.jsonl`, `concepts.jsonl`, `review_queue.json`,
`coverage.json`, and checkpoint files. These artifacts are draft material. They
are intended to support later review queues, GroundRecall promotion, source
coverage checks, and learner-facing study-aid construction without requiring
the person running ingestion to already know which claims or concepts are
important.

## Citation Extraction From Ingested Sources

After an ensemble ingestion pass, run a separate citation pass instead of
mixing citation extraction into source ingestion:

```sh
didactopus citations-from-ingest /path/to/run --out-dir /path/to/run/citation-extraction
```

The command reads `sources.jsonl` and `fragments.jsonl`, detects draft
reference-section entries, in-text author-year citations, and DOI-like spans,
and writes:

- `citation_link_manifest.json`;
- `reference_candidates.jsonl`;
- `reference_candidates.txt`;
- `in_text_citations.jsonl`;
- `citation_links.jsonl`;
- `citegeist_extracted.bib`;
- `citegeist_extracted.json`.

If CiteGeist is available, the pass also feeds detected reference blocks to
CiteGeist's extraction layer. When Didactopus is not running in the CiteGeist
virtual environment, the command falls back to CiteGeist's repo-local
`.venv/bin/python` when present. Malformed draft references are retained in
`citegeist_extracted.json` with render errors rather than aborting the whole
pass.

These outputs are draft citation-support artifacts. A reference candidate is
not a verified work identity, and an in-text citation occurrence is not proof
that the cited work supports the associated claim. Promotion requires review of
source identity, metadata, local source anchors, and the support relation.
