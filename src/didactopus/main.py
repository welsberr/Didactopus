from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import load_config
from .ai_learner_benchmark import run_benchmark as run_ai_learner_benchmark
from .source_spine_transfer_experiment import run_experiment as run_source_spine_transfer_experiment
from .provider_inspect import inspect_provider
from .notebook_learning_sequence import (
    DEFAULT_NOTEBOOK_ROOT,
    DEFAULT_SELECTION_POLICY_PATH,
    DEFAULT_SEQUENCE_PATH,
    build_notebook_sequence_session_plan,
)
from .citegeist_okf import write_citegeist_okf_source_bundle
from .citation_extract import run_citations_from_ingest
from .ensemble_ingest import run_ensemble_ingest
from .interoperability import registry_payload, validate_pack_capsule, write_registry
from .review_loader import load_draft_pack
from .review_schema import ReviewSession, ReviewAction
from .review_actions import apply_action
from .review_export import export_review_state_json, export_promoted_pack, export_review_ui_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus command-line tools")
    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review", help="Run the interactive review workflow scaffold")
    review_parser.add_argument("--draft-pack", required=True, help="Path to draft pack directory")
    review_parser.add_argument("--output-dir", default="review-output")
    review_parser.add_argument("--config", default="configs/config.example.yaml")

    inspect_parser = subparsers.add_parser("provider-inspect", help="Inspect provider routing, overrides, and resolved routes")
    inspect_parser.add_argument("--config", default="configs/config.geniehive.example.yaml")
    inspect_parser.add_argument("--kind", default="chat")
    inspect_parser.add_argument("--out")

    sequence_parser = subparsers.add_parser(
        "sequence-plan",
        help="Build a mentorship-oriented session plan from a Notebook learning-sequence artifact",
    )
    sequence_parser.add_argument(
        "--sequence",
        default=str(DEFAULT_SEQUENCE_PATH),
        help="Path to a Didactopus learning-sequence JSON artifact",
    )
    sequence_parser.add_argument(
        "--notebook-root",
        default=str(DEFAULT_NOTEBOOK_ROOT),
        help="Root used to resolve scaffold paths referenced by the sequence",
    )
    sequence_parser.add_argument(
        "--selection-policy",
        default=str(DEFAULT_SELECTION_POLICY_PATH),
        help="Scaffold selection-policy JSON; pass an empty string to disable policy ranking",
    )
    sequence_parser.add_argument("--learner-goal", help="Optional explicit learner goal to include in the session plan")
    sequence_parser.add_argument("--out", help="Optional output JSON path")

    citegeist_okf_parser = subparsers.add_parser(
        "citegeist-okf-source-corpus",
        help="Convert a CiteGeist OKF bundle into Didactopus source-corpus artifacts",
    )
    citegeist_okf_parser.add_argument("bundle_dir", help="Path to CiteGeist OKF bundle")
    citegeist_okf_parser.add_argument("out_dir", help="Directory to write Didactopus source-corpus artifacts")

    ensemble_parser = subparsers.add_parser(
        "ingest-ensemble",
        help="Run complete non-interactive ingestion over a file or source tree",
    )
    ensemble_parser.add_argument("source_root", help="Source file or directory to ingest")
    ensemble_parser.add_argument("--out-dir", required=True, help="Directory to write ensemble ingest artifacts")
    ensemble_parser.add_argument("--ingest-id", help="Stable ingest id for output manifests")
    ensemble_parser.add_argument("--display-root", help="Root used to render relative source paths")
    ensemble_parser.add_argument("--checkpoint-every", choices=["none", "file", "chunk"], default="chunk")
    ensemble_parser.add_argument("--max-chunk-chars", type=int, default=3000)

    citations_parser = subparsers.add_parser(
        "citations-from-ingest",
        help="Extract draft citation and reference candidates from ensemble ingestion artifacts",
    )
    citations_parser.add_argument("ingest_dir", help="Ensemble ingestion run directory or parent directory")
    citations_parser.add_argument("--out-dir", help="Directory to write citation-link artifacts")
    citations_parser.add_argument("--run-id", help="Stable citation extraction run id")
    citations_parser.add_argument("--citegeist-src", help="Path to CiteGeist src directory")
    citations_parser.add_argument("--citegeist-backend", default="heuristic", help="CiteGeist extraction backend")
    citations_parser.add_argument("--no-citegeist", action="store_true", help="Skip optional CiteGeist BibTeX extraction")
    citations_parser.add_argument("--max-fragments", type=int, help="Limit fragments processed for tests or previews")

    ai_bench_parser = subparsers.add_parser(
        "ai-learner-benchmark",
        help="Run a compact local-LLM AI learner mentorship benchmark",
    )
    ai_bench_parser.add_argument("--models", nargs="+", default=["gemma4:e4b", "qwen3:30b"])
    ai_bench_parser.add_argument("--out-dir", default="examples/ai-learner-mentorship/glass-orchard-latest")
    ai_bench_parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    ai_bench_parser.add_argument("--timeout", type=float, default=240.0)

    transfer_parser = subparsers.add_parser(
        "source-spine-transfer",
        help="Run a multi-condition source-spine transfer mentorship experiment",
    )
    transfer_parser.add_argument("--models", nargs="+", default=["gemma4:e4b", "qwen3:30b"])
    transfer_parser.add_argument(
        "--conditions",
        nargs="+",
        default=["source_dump", "summary_only", "full_didactopus", "causal_timing_calibration"],
    )
    transfer_parser.add_argument("--out-dir", default="examples/ai-learner-mentorship/source-spine-transfer-latest")
    transfer_parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    transfer_parser.add_argument("--timeout", type=float, default=240.0)

    registry_parser = subparsers.add_parser(
        "interoperability-registry",
        help="Print the standards registry and internal-object crosswalk",
    )
    registry_parser.add_argument("--out", help="Optional JSON output path")

    capsule_parser = subparsers.add_parser(
        "pack-capsule-validate",
        help="Validate a Didactopus pack capsule manifest JSON file",
    )
    capsule_parser.add_argument("manifest", help="Path to didactopus-pack-capsule manifest JSON")

    parser.set_defaults(command="review")
    return parser


def _run_review(args: argparse.Namespace) -> None:
    config = load_config(Path(args.config))
    draft = load_draft_pack(args.draft_pack)
    session = ReviewSession(reviewer=config.review.default_reviewer, draft_pack=draft)

    if session.draft_pack.concepts:
        first = session.draft_pack.concepts[0].concept_id
        apply_action(session, session.reviewer, ReviewAction(
            action_type="set_status",
            target=first,
            payload={"status": "trusted"},
            rationale="Initial concept appears well grounded.",
        ))
        apply_action(session, session.reviewer, ReviewAction(
            action_type="note",
            target=first,
            payload={"note": "Reviewed in initial curation pass."},
            rationale="Record reviewer note.",
        ))

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    export_review_state_json(session, outdir / "review_session.json")
    export_review_ui_data(session, outdir)

    if config.review.write_promoted_pack:
        export_promoted_pack(session, outdir / "promoted_pack")

    print("== Didactopus Interactive Review Workflow ==")
    print(f"Draft pack: {args.draft_pack}")
    print(f"Reviewer: {session.reviewer}")
    print(f"Concepts: {len(session.draft_pack.concepts)}")
    print(f"Ledger entries: {len(session.ledger)}")
    print(f"Output dir: {outdir}")


def _run_provider_inspect(args: argparse.Namespace) -> None:
    payload = inspect_provider(args.config, kind=args.kind, out_path=args.out)
    print(json.dumps(payload, indent=2))


def _run_sequence_plan(args: argparse.Namespace) -> None:
    payload = build_notebook_sequence_session_plan(
        args.sequence,
        learner_goal=args.learner_goal,
        notebook_root=args.notebook_root,
        selection_policy_path=args.selection_policy or None,
    )
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def _run_citegeist_okf_source_corpus(args: argparse.Namespace) -> None:
    payload = write_citegeist_okf_source_bundle(args.bundle_dir, args.out_dir)
    print(json.dumps(payload, indent=2))


def _run_ensemble_ingest(args: argparse.Namespace) -> None:
    try:
        result = run_ensemble_ingest(
            source_root=args.source_root,
            out_dir=args.out_dir,
            ingest_id=args.ingest_id,
            display_root=args.display_root,
            checkpoint_every=args.checkpoint_every,
            max_chunk_chars=args.max_chunk_chars,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"ingest-ensemble: {exc}") from None
    print(
        json.dumps(
            {
                "ingest_id": result.manifest["ingest_id"],
                "out_dir": str(result.out_dir),
                "counts": result.manifest["counts"],
                "artifacts": result.artifacts,
            },
            indent=2,
        )
    )


def _run_citations_from_ingest(args: argparse.Namespace) -> None:
    try:
        result = run_citations_from_ingest(
            ingest_dir=args.ingest_dir,
            out_dir=args.out_dir,
            run_id=args.run_id,
            citegeist_src=args.citegeist_src,
            citegeist_backend=args.citegeist_backend,
            use_citegeist=not args.no_citegeist,
            max_fragments=args.max_fragments,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"citations-from-ingest: {exc}") from None
    print(
        json.dumps(
            {
                "run_id": result.manifest["run_id"],
                "out_dir": str(result.out_dir),
                "counts": result.manifest["counts"],
                "citegeist": result.manifest["citegeist"],
                "artifacts": result.artifacts,
            },
            indent=2,
        )
    )


def _run_ai_learner_benchmark(args: argparse.Namespace) -> None:
    payload = run_ai_learner_benchmark(
        models=args.models,
        out_dir=args.out_dir,
        ollama_base_url=args.ollama_base_url,
        timeout=args.timeout,
    )
    print(json.dumps({"run_id": payload["run_id"], "artifacts": payload["artifacts"]}, indent=2))


def _run_source_spine_transfer(args: argparse.Namespace) -> None:
    payload = run_source_spine_transfer_experiment(
        models=args.models,
        conditions=args.conditions,
        out_dir=args.out_dir,
        ollama_base_url=args.ollama_base_url,
        timeout=args.timeout,
    )
    print(json.dumps({"run_id": payload["run_id"], "artifacts": payload["artifacts"]}, indent=2))


def _run_interoperability_registry(args: argparse.Namespace) -> None:
    payload = write_registry(args.out) if args.out else registry_payload()
    print(json.dumps(payload, indent=2))


def _run_pack_capsule_validate(args: argparse.Namespace) -> None:
    print(json.dumps(validate_pack_capsule(args.manifest), indent=2))


def main() -> None:
    argv = sys.argv[1:]
    known_commands = {
        "review",
        "provider-inspect",
        "sequence-plan",
        "citegeist-okf-source-corpus",
        "ingest-ensemble",
        "citations-from-ingest",
        "ai-learner-benchmark",
        "source-spine-transfer",
        "interoperability-registry",
        "pack-capsule-validate",
    }
    if argv and argv[0] not in known_commands:
        argv = ["review", *argv]
    args = build_parser().parse_args(argv)
    if args.command == "provider-inspect":
        _run_provider_inspect(args)
        return
    if args.command == "sequence-plan":
        _run_sequence_plan(args)
        return
    if args.command == "citegeist-okf-source-corpus":
        _run_citegeist_okf_source_corpus(args)
        return
    if args.command == "ingest-ensemble":
        _run_ensemble_ingest(args)
        return
    if args.command == "citations-from-ingest":
        _run_citations_from_ingest(args)
        return
    if args.command == "ai-learner-benchmark":
        _run_ai_learner_benchmark(args)
        return
    if args.command == "source-spine-transfer":
        _run_source_spine_transfer(args)
        return
    if args.command == "interoperability-registry":
        _run_interoperability_registry(args)
        return
    if args.command == "pack-capsule-validate":
        _run_pack_capsule_validate(args)
        return
    _run_review(args)


if __name__ == "__main__":
    main()
