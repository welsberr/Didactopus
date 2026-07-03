# GroundRecall Assistant Integration Architecture

This document defines how GroundRecall should support Codex, Claude Code, and
future assistant environments without treating any single assistant as the
authoritative integration target.

## Design rule

GroundRecall core must be assistant-agnostic.

Assistant-specific formats are derived views over promoted GroundRecall objects,
not the canonical representation of knowledge.

## Why this boundary matters

If assistant-specific prompt packaging leaks into the core model too early,
GroundRecall becomes:

- harder to evolve
- harder to validate
- harder to sync across machines
- harder to support across multiple assistant environments

The stable boundary should instead be:

- canonical grounded knowledge objects in core
- assistant adapters at the edge

## Core vs adapter split

### Core GroundRecall responsibilities

These should remain assistant-neutral:

- schemas for `Source`, `Fragment`, `Artifact`, `Observation`, `Claim`,
  `Concept`, `Relation`, `ReviewCandidate`, and `PromotionRecord`
- provenance and confidence modeling
- contradiction and supersession handling
- linting and review queue generation
- review and promotion workflows
- persistent storage for promoted objects
- query and retrieval semantics
- sync and multi-machine consolidation
- canonical export formats

### Assistant adapter responsibilities

These should be adapter-specific:

- prompt/context packaging
- assistant-specific bundle layout
- memory-file rendering
- skill-file rendering
- assistant capability declarations
- token-budget shaping and truncation policy
- tool-specific metadata

## Canonical export contract

GroundRecall should export assistant-neutral artifacts first.

Recommended canonical exports:

- `groundrecall_snapshot.json`
- `claims.jsonl`
- `concepts.jsonl`
- `relations.jsonl`
- `provenance_manifest.json`
- `query_bundle.json`

Assistant adapters then derive secondary outputs from those canonical exports.

## Assistant adapter interface

GroundRecall should expose a small adapter protocol.

Example shape:

```python
class AssistantAdapter(Protocol):
    name: str

    def export_bundle(self, snapshot: dict, out_dir: Path) -> list[Path]:
        ...

    def build_context(self, query_result: dict) -> dict:
        ...

    def supported_capabilities(self) -> dict[str, bool]:
        ...
```

This is a strategy/plugin boundary. A small registry or factory is acceptable,
but the important architectural decision is the separation of concerns, not the
factory itself.

## Recommended package layout

Recommended modules:

- `didactopus.groundrecall.models`
- `didactopus.groundrecall.store`
- `didactopus.groundrecall.promotion`
- `didactopus.groundrecall.query`
- `didactopus.groundrecall.export`
- `didactopus.groundrecall.assistants.base`
- `didactopus.groundrecall.assistants.codex`
- `didactopus.groundrecall.assistants.claude_code`

## Export layering

Recommended filesystem layout:

- `exports/canonical/`
- `exports/assistants/codex/`
- `exports/assistants/claude-code/`

Canonical exports remain the durable interchange format.

Assistant exports remain reproducible derived artifacts.

## Query layering

The query layer should return assistant-neutral structures such as:

- relevant claims
- supporting fragments
- provenance
- contradictions
- supersessions
- confidence and recency
- suggested next actions

Adapters may then convert this payload into:

- Codex skill/context bundles
- Claude Code project memory/context bundles
- future assistant context packages

## Stability policy

GroundRecall should adopt these rules early:

1. No assistant-specific fields in canonical `Claim` or `Concept` objects.
2. No assistant-specific persistence formats as authoritative storage.
3. No review or promotion decisions based on assistant-specific packaging.
4. Assistant adapters may be added or removed without changing canonical objects.

## Migration implication

Current and future GroundRecall work should replace language like:

- "Codex-facing export"
- "Codex skill bundle"

with:

- "assistant adapter bundle"
- "assistant-facing export"
- "assistant-specific derived bundle"

Codex can still be one adapter and may remain the first implemented adapter, but
it should not define the system boundary.

## Immediate implementation impact

The next GroundRecall milestones should be interpreted as:

1. build assistant-neutral canonical models and storage
2. build review and promotion over canonical objects
3. build canonical query and export layers
4. add assistant adapters as thin renderers over those canonical outputs

This is the lowest-risk path for long-term stability.
