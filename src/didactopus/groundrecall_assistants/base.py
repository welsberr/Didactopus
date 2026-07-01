from __future__ import annotations

"""Legacy flat GroundRecall assistant adapter base module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.assistants.base`` for new code.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class AssistantAdapter(Protocol):
    name: str

    def export_bundle(self, snapshot: dict, query_bundles: list[dict], out_dir: str | Path) -> list[Path]:
        ...

    def build_context(self, query_result: dict) -> dict:
        ...

    def supported_capabilities(self) -> dict[str, bool]:
        ...


_REGISTRY: dict[str, AssistantAdapter] = {}


def register_assistant_adapter(adapter: AssistantAdapter) -> AssistantAdapter:
    _REGISTRY[adapter.name] = adapter
    return adapter


def get_assistant_adapter(name: str) -> AssistantAdapter:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"Unknown assistant adapter: {name}") from exc


def list_assistant_adapters() -> list[str]:
    return sorted(_REGISTRY)
