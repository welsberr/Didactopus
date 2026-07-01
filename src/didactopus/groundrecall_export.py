from __future__ import annotations

"""Legacy flat GroundRecall export module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.export`` or CLI usage via
``didactopus.groundrecall.cli`` for new code.
"""

from .groundrecall.export import (
    build_parser,
    export_canonical_bundle,
    export_canonical_snapshot,
    export_query_bundle,
    main,
)

__all__ = [
    "export_canonical_snapshot",
    "export_query_bundle",
    "export_canonical_bundle",
    "build_parser",
    "main",
]
