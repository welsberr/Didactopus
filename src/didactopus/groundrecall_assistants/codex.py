from __future__ import annotations

import json
from pathlib import Path

from .base import register_assistant_adapter


class CodexAdapter:
    name = "codex"

    def export_bundle(self, snapshot: dict, query_bundles: list[dict], out_dir: str | Path) -> list[Path]:
        target = Path(out_dir)
        target.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []

        skill_payload = {
            "name": f"groundrecall-{snapshot.get('snapshot_id', 'snapshot')}",
            "description": "GroundRecall assistant adapter bundle for Codex.",
            "snapshot_id": snapshot.get("snapshot_id", ""),
            "concept_count": len(snapshot.get("concepts", [])),
            "claim_count": len(snapshot.get("claims", [])),
        }
        skill_md = "\n".join(
            [
                "---",
                f"name: {skill_payload['name']}",
                f"description: {skill_payload['description']}",
                "---",
                "",
                "# GroundRecall Codex Bundle",
                "",
                f"- Snapshot: `{skill_payload['snapshot_id']}`",
                f"- Concepts: {skill_payload['concept_count']}",
                f"- Claims: {skill_payload['claim_count']}",
                "",
                "Use the accompanying canonical JSON and query bundles as the primary source of grounded context.",
            ]
        )
        skill_path = target / "SKILL.md"
        skill_path.write_text(skill_md, encoding="utf-8")
        paths.append(skill_path)

        bundle_path = target / "codex_bundle.json"
        bundle_path.write_text(
            json.dumps(
                {
                    "assistant": "codex",
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
            "assistant": "codex",
            "context_kind": "groundrecall_query_bundle",
            "concept": query_result.get("concept", {}),
            "relevant_claims": query_result.get("relevant_claims", []),
            "supporting_observations": query_result.get("supporting_observations", []),
            "suggested_next_actions": query_result.get("suggested_next_actions", []),
        }

    def supported_capabilities(self) -> dict[str, bool]:
        return {
            "skill_markdown": True,
            "json_bundle": True,
            "project_memory": False,
        }


register_assistant_adapter(CodexAdapter())
