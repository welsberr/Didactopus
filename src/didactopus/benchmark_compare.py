from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from epistemap import g_summary_comparison_from_files, write_g_summary_comparison_markdown


def compare_g_summary_files(
    summary_paths: Iterable[str | Path],
    *,
    baseline_id: str | None = None,
    out_path: str | Path | None = None,
    out_markdown_path: str | Path | None = None,
    require_compatible: bool = False,
) -> dict:
    """Compare Epistemap G summary JSON files produced by Didactopus runs."""

    comparison = g_summary_comparison_from_files(summary_paths, baseline_id=baseline_id, out_json=out_path)
    if out_markdown_path is not None:
        write_g_summary_comparison_markdown(comparison, out_markdown_path)
    if require_compatible and not comparison["compatibility"]["compatible"]:
        raise SystemExit(2)
    return comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Didactopus Epistemap G summary files.")
    parser.add_argument("summaries", nargs="+", help="Paths to *_g_summary.json files.")
    parser.add_argument("--baseline-id", default=None)
    parser.add_argument("--out", default=None, help="Optional output JSON path.")
    parser.add_argument("--out-md", default=None, help="Optional output Markdown report path.")
    parser.add_argument(
        "--require-compatible",
        action="store_true",
        help="Exit with status 2 if compatibility diagnostics contain warnings.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    comparison = compare_g_summary_files(
        args.summaries,
        baseline_id=args.baseline_id,
        out_path=args.out,
        out_markdown_path=args.out_md,
        require_compatible=args.require_compatible,
    )
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
