from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from epistemap import g_summary_comparison


def compare_g_summary_files(
    summary_paths: Iterable[str | Path],
    *,
    baseline_id: str | None = None,
    out_path: str | Path | None = None,
) -> dict:
    """Compare Epistemap G summary JSON files produced by Didactopus runs."""

    summaries = [json.loads(Path(path).read_text(encoding="utf-8")) for path in summary_paths]
    comparison = g_summary_comparison(summaries, baseline_id=baseline_id)
    if out_path is not None:
        destination = Path(out_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    return comparison


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
