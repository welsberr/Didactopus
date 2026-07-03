"""Legacy flat GroundRecall source adapter package.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.source_adapters`` for new code.
"""

from .base import get_source_adapter, list_source_adapters
from . import llmwiki  # noqa: F401
from . import markdown_notes  # noqa: F401
from . import transcript  # noqa: F401
from . import didactopus_pack  # noqa: F401

__all__ = ["get_source_adapter", "list_source_adapters"]
