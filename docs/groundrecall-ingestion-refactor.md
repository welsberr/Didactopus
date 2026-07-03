# GroundRecall Ingestion Refactor Plan

GroundRecall should treat `llmwiki` as one upstream source shape, not as the
defining architecture for grounded knowledge import.

Didactopus already has broader ambitions around ingestion of weakly structured
materials such as:

- markdown notes
- transcripts
- HTML/text course materials
- generated draft packs
- review sessions
- learner artifacts

The GroundRecall import pipeline should therefore be generalized around a shared
normalization and promotion substrate with pluggable source adapters.

## Design rule

Source-specific logic should live at the ingestion edge.

These stages should be generic:

- segmentation
- extraction
- normalization
- lint
- review queue generation
- review bridge
- promotion
- canonical store
- query
- canonical export

## Recommended module split

Recommended package layout:

- `didactopus.groundrecall_ingest`
- `didactopus.groundrecall_source_adapters.base`
- `didactopus.groundrecall_source_adapters.llmwiki`
- `didactopus.groundrecall_source_adapters.markdown_notes`
- `didactopus.groundrecall_source_adapters.transcript`
- `didactopus.groundrecall_source_adapters.didactopus_pack`
- `didactopus.groundrecall_source_adapters.didactopus_review`

## Shared intermediate envelope

Adapters should emit shared discovery records rather than jumping straight into
canonical GroundRecall objects.

Recommended intermediate types:

- `DiscoveredImportSource`
- `SegmentCandidate`
- `ImportProfile`

This keeps adapter-specific parsing separate from the shared import pipeline.

## Output intent

Not every imported source should be treated the same way.

Adapters should declare an output intent:

- `grounded_knowledge`
- `curriculum`
- `both`

Examples:

- `llmwiki` usually targets `grounded_knowledge`
- loose transcripts may target `grounded_knowledge`
- syllabus/course folders often target `curriculum`
- Didactopus packs or review sessions may target `both`

## First refactor milestones

### Milestone 1

- introduce adapter registry and adapter protocol
- move current `llmwiki` discovery/classification behind an adapter
- preserve the current import CLI behavior

### Milestone 2

- add a `markdown_notes` adapter
- add a `transcript` adapter
- add import profiles that tune extraction strictness

### Milestone 3

- add a `didactopus_pack` adapter for pack and review artifacts
- allow current Didactopus outputs to feed into GroundRecall directly

## Why this matters

This avoids building two parallel ingestion stacks inside Didactopus:

- one for packs and educational structures
- another for grounded knowledge capture

Instead, the system gets one generic ingestion substrate with multiple source
adapters and multiple downstream promotion/export paths.
