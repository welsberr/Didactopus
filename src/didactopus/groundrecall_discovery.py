from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".log",
}


@dataclass
class DiscoveredArtifact:
    path: Path
    relative_path: str
    artifact_kind: str
    is_text: bool


def classify_artifact(root: Path, path: Path) -> DiscoveredArtifact:
    rel = path.relative_to(root).as_posix()
    top = rel.split("/", 1)[0]
    suffix = path.suffix.lower()
    is_text = suffix in TEXT_EXTENSIONS or path.name in {"README", "LICENSE"}
    artifact_kind = "generic_artifact"
    if top == "wiki":
        artifact_kind = "compiled_page"
    elif top in {"raw", "sources"}:
        artifact_kind = "raw_note"
    elif top == "logs":
        artifact_kind = "session_log"
    elif path.name.startswith("schema."):
        artifact_kind = "schema_file"
    elif suffix in {".md", ".markdown"}:
        artifact_kind = "markdown_note"
    return DiscoveredArtifact(path=path, relative_path=rel, artifact_kind=artifact_kind, is_text=is_text)


def discover_llmwiki_artifacts(root: str | Path) -> list[DiscoveredArtifact]:
    base = Path(root)
    artifacts: list[DiscoveredArtifact] = []
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        artifacts.append(classify_artifact(base, path))
    return artifacts
