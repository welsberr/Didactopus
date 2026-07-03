from __future__ import annotations

"""Legacy flat GroundRecall source adapter base module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.source_adapters.base`` for new
code.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol


ImportIntent = Literal["grounded_knowledge", "curriculum", "both"]


@dataclass
class DiscoveredImportSource:
    path: Path
    relative_path: str
    source_kind: str
    artifact_kind: str
    is_text: bool
    metadata: dict


@dataclass
class StructuredImportRows:
    artifact_rows: list[dict]
    observation_rows: list[dict]
    claim_rows: list[dict]
    concept_rows: list[dict]
    relation_rows: list[dict]


class GroundRecallSourceAdapter(Protocol):
    name: str

    def detect(self, root: str | Path) -> bool:
        ...

    def discover(self, root: str | Path) -> list[DiscoveredImportSource]:
        ...

    def import_intent(self) -> ImportIntent:
        ...

    def build_rows(self, context, sources: list[DiscoveredImportSource]) -> StructuredImportRows | None:
        ...


_REGISTRY: dict[str, GroundRecallSourceAdapter] = {}


def register_source_adapter(adapter: GroundRecallSourceAdapter) -> GroundRecallSourceAdapter:
    _REGISTRY[adapter.name] = adapter
    return adapter


def get_source_adapter(name: str) -> GroundRecallSourceAdapter:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"Unknown GroundRecall source adapter: {name}") from exc


def list_source_adapters() -> list[str]:
    return sorted(_REGISTRY)


def detect_source_adapter(root: str | Path) -> GroundRecallSourceAdapter:
    for name in list_source_adapters():
        adapter = _REGISTRY[name]
        if adapter.detect(root):
            return adapter
    raise ValueError(f"No GroundRecall source adapter detected for {root}")
