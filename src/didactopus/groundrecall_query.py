from __future__ import annotations

"""Legacy flat GroundRecall query module.

Compatibility path retained during the internal namespace migration.
Prefer imports under ``didactopus.groundrecall.query`` or CLI usage via
``didactopus.groundrecall.cli`` for new code.
"""

from .groundrecall.query import (
    build_parser,
    build_query_bundle_for_concept,
    main,
    query_concept,
    query_provenance,
    search_claims,
)

__all__ = [
    "query_concept",
    "search_claims",
    "query_provenance",
    "build_query_bundle_for_concept",
    "build_parser",
    "main",
]
