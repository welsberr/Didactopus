from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .doclift_bundle_demo import run_doclift_bundle_demo
from .groundrecall_pack_bridge import run_doclift_bundle_with_groundrecall
from .augmentation_bundle_probe import write_probe_report
from .archive_phrase_inventory import write_archive_phrase_inventory_report
from .first_ring_batch_promotion import run_first_ring_batch_promotion
from .notebook_page import export_notebook_page_from_groundrecall_bundle
from .notebook_page import export_notebook_page_from_groundrecall_store
from .review_loader import load_draft_pack
from .review_schema import ReviewSession, ReviewAction
from .review_actions import apply_action
from .review_export import export_review_state_json, export_promoted_pack, export_review_ui_data


def build_review_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus interactive review workflow scaffold")
    parser.add_argument("--draft-pack", required=True, help="Path to draft pack directory")
    parser.add_argument("--output-dir", default="review-output")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus command-line tools")
    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review", help="Run the interactive review workflow scaffold")
    review_parser.add_argument("--draft-pack", required=True, help="Path to draft pack directory")
    review_parser.add_argument("--output-dir", default="review-output")
    review_parser.add_argument("--config", default="configs/config.example.yaml")

    doclift_parser = subparsers.add_parser("doclift-bundle", help="Generate a draft pack from a doclift bundle")
    doclift_parser.add_argument("bundle_dir")
    doclift_parser.add_argument("pack_dir")
    doclift_parser.add_argument("--course-title", required=True)
    doclift_parser.add_argument("--author", default="doclift bundle import")
    doclift_parser.add_argument("--license-name", default="See source bundle metadata")

    doclift_gr_parser = subparsers.add_parser(
        "doclift-bundle-groundrecall",
        help="Generate a draft pack from a doclift bundle using a GroundRecall concept query bundle",
    )
    doclift_gr_parser.add_argument("groundrecall_store_dir")
    doclift_gr_parser.add_argument("groundrecall_concept_ref")
    doclift_gr_parser.add_argument("bundle_dir")
    doclift_gr_parser.add_argument("pack_dir")
    doclift_gr_parser.add_argument("--course-title", required=True)
    doclift_gr_parser.add_argument("--author", default="doclift bundle import")
    doclift_gr_parser.add_argument("--license-name", default="See source bundle metadata")

    notebook_parser = subparsers.add_parser(
        "notebook-page",
        help="Build a Notebook page payload from a GroundRecall query bundle",
    )
    notebook_parser.add_argument("groundrecall_query_bundle")
    notebook_parser.add_argument("output_path")

    notebook_gr_parser = subparsers.add_parser(
        "notebook-page-groundrecall",
        help="Build a Notebook page and query bundle directly from a GroundRecall concept",
    )
    notebook_gr_parser.add_argument("groundrecall_store_dir")
    notebook_gr_parser.add_argument("groundrecall_concept_ref")
    notebook_gr_parser.add_argument("output_dir")

    augmentation_probe_parser = subparsers.add_parser(
        "augmentation-bundle-probe",
        help="Probe an augmentation bundle against an existing GroundRecall query bundle",
    )
    augmentation_probe_parser.add_argument("augmentation_bundle")
    augmentation_probe_parser.add_argument("groundrecall_query_bundle")
    augmentation_probe_parser.add_argument("output_path")

    phrase_inventory_parser = subparsers.add_parser(
        "archive-phrase-inventory",
        help="Extract and rank repeated phrase candidates from archive-style source bundles",
    )
    phrase_inventory_parser.add_argument("output_path")
    phrase_inventory_parser.add_argument("input_paths", nargs="+")
    phrase_inventory_parser.add_argument("--seed-term", action="append", default=[])
    phrase_inventory_parser.add_argument("--top-n", type=int, default=50)

    first_ring_parser = subparsers.add_parser(
        "first-ring-batch-promotion",
        help="Batch-promote first-ring query bundles from a manifest and canonical bundle set",
    )
    first_ring_parser.add_argument("manifest_path")
    first_ring_parser.add_argument("canonical_dir")
    first_ring_parser.add_argument("--output-dir")
    return parser


def run_review_workflow(args: argparse.Namespace) -> None:
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


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        args = build_review_parser().parse_args(argv)
        run_review_workflow(args)
        return

    args = build_parser().parse_args(argv)
    if args.command == "review":
        run_review_workflow(args)
        return
    if args.command == "doclift-bundle":
        summary = run_doclift_bundle_demo(
            bundle_dir=args.bundle_dir,
            course_title=args.course_title,
            pack_dir=args.pack_dir,
            author=args.author,
            license_name=args.license_name,
        )
        print(summary)
        return
    if args.command == "doclift-bundle-groundrecall":
        summary = run_doclift_bundle_with_groundrecall(
            groundrecall_store_dir=args.groundrecall_store_dir,
            groundrecall_concept_ref=args.groundrecall_concept_ref,
            bundle_dir=args.bundle_dir,
            course_title=args.course_title,
            pack_dir=args.pack_dir,
            author=args.author,
            license_name=args.license_name,
        )
        print(summary)
        return
    if args.command == "notebook-page":
        summary = export_notebook_page_from_groundrecall_bundle(
            args.groundrecall_query_bundle,
            args.output_path,
        )
        print(summary)
        return
    if args.command == "notebook-page-groundrecall":
        summary = export_notebook_page_from_groundrecall_store(
            args.groundrecall_store_dir,
            args.groundrecall_concept_ref,
            args.output_dir,
        )
        print(summary)
        return
    if args.command == "augmentation-bundle-probe":
        summary = write_probe_report(
            args.augmentation_bundle,
            args.groundrecall_query_bundle,
            args.output_path,
        )
        print(summary)
        return
    if args.command == "archive-phrase-inventory":
        summary = write_archive_phrase_inventory_report(
            args.input_paths,
            args.output_path,
            seed_terms=args.seed_term,
            top_n=args.top_n,
        )
        print(summary)
        return
    if args.command == "first-ring-batch-promotion":
        summary = run_first_ring_batch_promotion(
            args.manifest_path,
            args.canonical_dir,
            args.output_dir,
        )
        print(summary)
        return
    build_parser().print_help()
