from __future__ import annotations

from pathlib import Path

from .base import DiscoveredImportSource, StructuredImportRows, register_source_adapter


TEXT_SUFFIXES = {".md", ".markdown", ".txt"}


class MarkdownNotesSourceAdapter:
    name = "markdown_notes"

    def detect(self, root: str | Path) -> bool:
        base = Path(root)
        return any(path.suffix.lower() in TEXT_SUFFIXES for path in base.rglob("*") if path.is_file())

    def discover(self, root: str | Path) -> list[DiscoveredImportSource]:
        base = Path(root)
        rows: list[DiscoveredImportSource] = []
        for path in sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES):
            rows.append(
                DiscoveredImportSource(
                    path=path,
                    relative_path=path.relative_to(base).as_posix(),
                    source_kind="markdown_notes",
                    artifact_kind="markdown_note",
                    is_text=True,
                    metadata={},
                )
            )
        return rows

    def import_intent(self) -> str:
        return "grounded_knowledge"

    def build_rows(self, context, sources: list[DiscoveredImportSource]) -> StructuredImportRows | None:
        return None


register_source_adapter(MarkdownNotesSourceAdapter())
