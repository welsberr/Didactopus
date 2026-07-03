from __future__ import annotations

"""Legacy flat GroundRecall assistant export module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.assistant_export`` or CLI usage
via ``didactopus.groundrecall.cli`` for new code.
"""

from .groundrecall.assistant_export import build_parser, export_assistant_bundle, main

__all__ = ["export_assistant_bundle", "build_parser", "main"]
