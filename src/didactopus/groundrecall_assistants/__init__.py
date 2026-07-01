"""Legacy flat GroundRecall assistants package.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.assistants`` for new code.
"""

from .base import get_assistant_adapter, list_assistant_adapters

__all__ = ["get_assistant_adapter", "list_assistant_adapters"]
