# GroundRecall `llmwiki` Import Specification

This document defines the first-pass import path for users who already have some
form of `llmwiki`-style repository and want to migrate it into the broader
GroundRecall substrate while staying compatible with Didactopus review and
promotion flows.

## Goal

The import path should let an existing `llmwiki` corpus become:

- searchable without immediate manual cleanup
- reviewable rather than blindly trusted
- grounded in explicit provenance
- promotable into durable structured knowledge objects
- exportable back into compiled wiki pages, assistant adapter bundles, and
  queryable graph artifacts

The key rule is:

Imported wiki pages are **derived artifacts**, not automatic source truth.

## Import philosophy

Users coming from `llmwiki` often have a mixture of:

- raw notes
- compiled markdown pages
- local source files
- generated summaries
- ad hoc link graphs
- session transcripts
- speculative or weakly-supported synthesis

GroundRecall should preserve that work without pretending all of it is already
promoted knowledge.

The import pipeline therefore has two responsibilities:

1. Preserve the original material with minimal loss.
2. Reify explicit structured objects that can later be reviewed and promoted.

## Scope of the first implementation

The first implementation should support common `llmwiki` layouts such as:

- `raw/`
- `wiki/`
- `schema.*`
- `logs/`
- `sources/`
- top-level markdown pages

The importer should not require a canonical upstream schema. It should operate
from directory conventions plus simple heuristics.

## Import modes

### 1. `archive`

Purpose:
- preserve an existing `llmwiki` tree as read-only imported artifacts
- index it for search and later review

Behavior:
- no claim promotion
- minimal extraction
- all compiled pages remain `draft`

Use when:
- the user wants backward compatibility first
- the corpus quality is unknown

### 2. `quick`

Purpose:
- bootstrap usable structured objects fast

Behavior:
- import pages and raw sources
- extract candidate claims and concepts heuristically
- attach lightweight provenance
- queue uncertain items for review

Use when:
- the user wants early utility and accepts heuristic noise

### 3. `grounded`

Purpose:
- perform a migration suitable for long-lived shared knowledge

Behavior:
- require provenance for promoted claims
- mark unsupported statements explicitly
- produce review records and lint findings
- populate promotion queues rather than auto-promoting

Use when:
- the imported corpus will be shared across machines or agents

## Pipeline stages

### 1. Capture

The importer records the source repository as an import artifact.

Required metadata:

- `import_id`
- `import_mode`
- `source_root`
- `imported_at`
- `machine_id`
- `agent_id`
- `source_repo_kind=llmwiki`

Outputs:

- import manifest
- artifact records for all discovered files

### 2. Segment

Imported content is split into stable units.

Primary segment types:

- `source_document`
- `source_fragment`
- `compiled_page`
- `section_summary`
- `candidate_claim`
- `candidate_concept`
- `candidate_relation`
- `session_observation`

Segmentation should preserve:

- original path
- section heading
- line or byte offsets when possible
- page title
- frontmatter fields

### 3. Classify

Each segment gets a semantic role.

Recommended roles:

- `source`
- `derivation`
- `claim`
- `summary`
- `question`
- `todo`
- `speculation`
- `obsolete`
- `transcript`

This prevents unsupported prose from being confused with grounded knowledge.

### 4. Ground

Each imported segment gets provenance and support metadata.

Required grounding fields:

- `origin_artifact_id`
- `origin_path`
- `origin_section`
- `source_url` when known
- `retrieval_date` when known
- `machine_id`
- `session_id` when known
- `support_kind`
- `grounding_status`

Suggested values:

- `support_kind`: `direct_source`, `derived_from_page`, `derived_from_session`,
  `inferred`, `unknown`
- `grounding_status`: `grounded`, `partially_grounded`, `ungrounded`

### 5. Normalize

The importer emits explicit GroundRecall objects.

Minimum object set:

- `Source`
- `Fragment`
- `Artifact`
- `Observation`
- `Claim`
- `Concept`
- `Relation`

### 6. Lint

The importer produces machine-readable findings before promotion.

Required lint checks:

- claim has no supporting fragment
- multiple claims appear text-identical
- concept is orphaned
- relation points to missing concept
- page summary has no cited support
- imported item marked `obsolete` still linked as current
- same claim imported with conflicting confidence or polarity

### 7. Promote

Imported objects enter existing Didactopus review/promotion lanes rather than
becoming trusted immediately.

Recommended states:

- `draft`
- `triaged`
- `reviewed`
- `promoted`
- `superseded`
- `archived`

### 8. Export

Promoted objects can then be rendered back out as:

- compiled wiki pages
- graph snapshots
- assistant adapter bundles
- review reports
- query bundles for assistant-facing use

## Object contracts

### `ImportedArtifact`

```json
{
  "artifact_id": "ia_001",
  "import_id": "imp_2026_04_16_a",
  "artifact_kind": "compiled_page",
  "path": "wiki/channel-capacity.md",
  "title": "Channel Capacity",
  "sha256": "abc123",
  "created_at": "2026-04-16T14:00:00Z",
  "metadata": {
    "frontmatter": {},
    "headings": ["Definition", "Examples"]
  },
  "current_status": "draft"
}
```

### `ImportedObservation`

```json
{
  "observation_id": "obs_001",
  "import_id": "imp_2026_04_16_a",
  "artifact_id": "ia_001",
  "role": "summary",
  "text": "Capacity bounds reliable communication over a noisy channel.",
  "origin_path": "wiki/channel-capacity.md",
  "origin_section": "Definition",
  "line_start": 12,
  "line_end": 14,
  "grounding_status": "partially_grounded",
  "support_kind": "derived_from_page",
  "confidence_hint": 0.63,
  "current_status": "draft"
}
```

### `ImportedClaim`

```json
{
  "claim_id": "clm_001",
  "import_id": "imp_2026_04_16_a",
  "claim_text": "Channel capacity is the maximum reliable communication rate for a channel model.",
  "claim_kind": "definition",
  "source_observation_ids": ["obs_001"],
  "supporting_fragment_ids": ["frag_014"],
  "concept_ids": ["concept::channel-capacity"],
  "confidence_hint": 0.74,
  "grounding_status": "grounded",
  "current_status": "triaged"
}
```

### `ImportedConcept`

```json
{
  "concept_id": "concept::channel-capacity",
  "import_id": "imp_2026_04_16_a",
  "title": "Channel Capacity",
  "aliases": [],
  "description": "Imported concept from llmwiki corpus.",
  "source_artifact_ids": ["ia_001"],
  "current_status": "triaged"
}
```

### `ImportedRelation`

```json
{
  "relation_id": "rel_001",
  "import_id": "imp_2026_04_16_a",
  "source_id": "concept::shannon-entropy",
  "target_id": "concept::channel-capacity",
  "relation_type": "supports_understanding_of",
  "evidence_ids": ["obs_015"],
  "current_status": "draft"
}
```

## Mapping from `llmwiki` into GroundRecall

Recommended first-pass mapping:

- `raw/*` -> `Source` or `Artifact(kind=raw_note)`
- `wiki/*.md` -> `Artifact(kind=compiled_page)`
- frontmatter -> artifact metadata
- headings -> section boundaries
- linked page names -> candidate `Concept` and `Relation`
- bullet or sentence extraction -> candidate `Observation` and `Claim`
- chat or session logs -> `Observation(kind=session_note)`
- schema files -> import metadata only unless a future adapter exists

## Confidence and trust policy

Imported confidence must remain clearly separate from reviewed confidence.

Recommended fields:

- `confidence_hint`
- `review_confidence`
- `grounding_status`
- `review_verdict`

Policy:

- `confidence_hint` comes from heuristic import scoring
- `review_confidence` exists only after review
- promotion requires at least `partially_grounded`
- fully ungrounded claims can be stored, but only as `draft` or `archived`

## Provenance policy

The importer should follow the existing Didactopus provenance direction:

- preserve source identity
- preserve retrieval date when available
- preserve adaptation status
- keep both human-readable and machine-readable provenance

When only a compiled wiki page exists and the original source is missing:

- the compiled page becomes the immediate origin artifact
- all extracted claims must be marked `derived_from_page`
- such claims should not auto-promote in `grounded` mode

## Review and promotion integration

Imported `Claim` and `Concept` objects should feed into the same general review
machinery already used for pack-oriented promotion:

- create candidate records
- attach lint findings
- route to a triage lane
- collect review verdicts
- emit promotion records

Suggested triage lanes:

- `knowledge_capture`
- `pack_improvement`
- `skill_export`
- `source_cleanup`
- `conflict_resolution`

## Module layout

First-pass module layout:

- `didactopus.groundrecall_import`
  Entry points and top-level orchestration.
- `didactopus.groundrecall_discovery`
  Finds `llmwiki`-style files and classifies paths.
- `didactopus.groundrecall_segmenter`
  Splits pages and logs into stable observations and candidate claims.
- `didactopus.groundrecall_normalizer`
  Emits normalized import objects.
- `didactopus.groundrecall_lint`
  Import-time lint checks.
- `didactopus.groundrecall_review_bridge`
  Converts imported objects into review candidates and promotion records.
- `didactopus.groundrecall_export`
  Renders promoted objects back to wiki, graph, and skill artifacts.

## CLI shape

Suggested CLI:

```bash
python -m didactopus.groundrecall.cli import /path/to/llmwiki --mode archive
python -m didactopus.groundrecall.cli import /path/to/llmwiki --mode quick
python -m didactopus.groundrecall.cli import /path/to/llmwiki --mode grounded
python -m didactopus.groundrecall.cli lint imports/<import-id>
python -m didactopus.groundrecall.cli promote imports/<import-id> /path/to/store
python -m didactopus.groundrecall.cli export /path/to/store exports/groundrecall --concept channel-capacity
```

Compatibility wrappers still exist during migration:

```bash
python -m didactopus.groundrecall_import /path/to/llmwiki --mode grounded
python -m didactopus.groundrecall_lint imports/<import-id>
python -m didactopus.groundrecall_export /path/to/store exports/groundrecall --concept channel-capacity
```

## Filesystem layout

Suggested repository-local layout:

- `imports/<import-id>/manifest.json`
- `imports/<import-id>/artifacts.jsonl`
- `imports/<import-id>/observations.jsonl`
- `imports/<import-id>/claims.jsonl`
- `imports/<import-id>/concepts.jsonl`
- `imports/<import-id>/relations.jsonl`
- `imports/<import-id>/lint_findings.json`
- `imports/<import-id>/review_queue.json`

This keeps imported state auditable and easy to sync across machines.

## Multi-machine sync implication

For distributed assistant use, imported state should be append-oriented and
rebuildable.

Recommended sync primitives:

- import manifests
- normalized jsonl object streams
- review records
- promotion records

Non-authoritative derived artifacts:

- rendered wiki pages
- local indexes
- embeddings
- cache files

This allows multiple machines to contribute import events without making the
compiled page tree the merge primitive.

## First implementation milestones

### Milestone 1

- discover `raw/` and `wiki/`
- import artifacts
- segment markdown by headings
- emit observations and candidate claims
- write import manifest and jsonl outputs

### Milestone 2

- add grounding metadata
- add lint checks
- add triage lanes and review queue output

### Milestone 3

- map promoted claims into assistant-neutral exports plus assistant adapter bundles
- render compiled wiki views from promoted objects
- support multi-machine import manifests and merge-safe event storage

## Non-goals for the first pass

- perfect semantic claim extraction
- automatic trust assignment
- full upstream `llmwiki` schema compatibility
- lossless import of every custom plugin or script
- embeddings-first retrieval

The first pass should be conservative, inspectable, and easy to improve.
