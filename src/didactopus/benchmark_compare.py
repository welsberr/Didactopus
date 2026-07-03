from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from epistemap import g_summary_comparison_from_files


def compare_g_summary_files(
    summary_paths: Iterable[str | Path],
    *,
    baseline_id: str | None = None,
    out_path: str | Path | None = None,
) -> dict:
    """Compare Epistemap G summary JSON files produced by Didactopus runs."""

    return g_summary_comparison_from_files(summary_paths, baseline_id=baseline_id, out_json=out_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Didactopus Epistemap G summary files.")
    parser.add_argument("summaries", nargs="+", help="Paths to *_g_summary.json files.")
    parser.add_argument("--baseline-id", default=None)
    parser.add_argument("--out", default=None, help="Optional output JSON path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    comparison = compare_g_summary_files(
        args.summaries,
        baseline_id=args.baseline_id,
        out_path=args.out,
    )
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
