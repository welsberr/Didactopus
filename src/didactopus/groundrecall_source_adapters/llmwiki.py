from __future__ import annotations

from pathlib import Path

from ..groundrecall_discovery import discover_llmwiki_artifacts
from .base import DiscoveredImportSource, StructuredImportRows, register_source_adapter


class LLMWikiSourceAdapter:
    name = "llmwiki"

    def detect(self, root: str | Path) -> bool:
        base = Path(root)
        return (base / "wiki").exists() or (base / "raw").exists() or any(path.name.startswith("schema.") for path in base.iterdir() if path.exists())

    def discover(self, root: str | Path) -> list[DiscoveredImportSource]:
        return [
            DiscoveredImportSource(
                path=item.path,
                relative_path=item.relative_path,
                source_kind="llmwiki",
                artifact_kind=item.artifact_kind,
                is_text=item.is_text,
                metadata={},
            )
            for item in discover_llmwiki_artifacts(root)
        ]

    def import_intent(self) -> str:
        return "grounded_knowledge"

    def build_rows(self, context, sources: list[DiscoveredImportSource]) -> StructuredImportRows | None:
        return None


register_source_adapter(LLMWikiSourceAdapter())
