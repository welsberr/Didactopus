from __future__ import annotations

import json
from pathlib import Path

from .base import register_assistant_adapter


class ClaudeCodeAdapter:
    name = "claude_code"

    def export_bundle(self, snapshot: dict, query_bundles: list[dict], out_dir: str | Path) -> list[Path]:
        target = Path(out_dir)
        target.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []

        memory_md = "\n".join(
            [
                "# GroundRecall Memory",
                "",
                f"- Snapshot: `{snapshot.get('snapshot_id', '')}`",
                f"- Concepts: {len(snapshot.get('concepts', []))}",
                f"- Claims: {len(snapshot.get('claims', []))}",
                "",
                "Prefer the canonical GroundRecall snapshot and query bundles over free-form recollection.",
                "",
                "## Query Bundles",
            ]
            + [f"- `{bundle.get('concept', {}).get('concept_id', 'unknown')}`" for bundle in query_bundles]
        )
        memory_path = target / "CLAUDE.md"
        memory_path.write_text(memory_md, encoding="utf-8")
        paths.append(memory_path)

        bundle_path = target / "claude_code_bundle.json"
        bundle_path.write_text(
            json.dumps(
                {
                    "assistant": "claude_code",
                    "snapshot_id": snapshot.get("snapshot_id", ""),
                    "query_bundle_count": len(query_bundles),
                    "query_bundles": query_bundles,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        paths.append(bundle_path)
        return paths

    def build_context(self, query_result: dict) -> dict:
        return {
            "assistant": "claude_code",
            "memory_kind": "groundrecall_query_bundle",
            "concept": query_result.get("concept", {}),
            "claims": query_result.get("relevant_claims", []),
            "support": query_result.get("supporting_observations", []),
            "next_actions": query_result.get("suggested_next_actions", []),
        }

    def supported_capabilities(self) -> dict[str, bool]:
        return {
            "skill_markdown": False,
            "json_bundle": True,
            "project_memory": True,
        }


register_assistant_adapter(ClaudeCodeAdapter())
