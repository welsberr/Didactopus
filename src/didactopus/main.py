from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .review_loader import load_draft_pack
from .review_schema import ReviewSession, ReviewAction
from .review_actions import apply_action
from .review_export import export_review_state_json, export_promoted_pack, export_review_ui_data
from .ui_scaffold import write_review_ui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus review workflow scaffold")
    parser.add_argument("--draft-pack", required=True, help="Path to draft pack directory")
    parser.add_argument("--output-dir", default="review-output")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    draft = load_draft_pack(args.draft_pack)
    session = ReviewSession(reviewer=config.review.default_reviewer, draft_pack=draft)

    # Demo curation actions
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

    if len(session.draft_pack.concepts) > 1:
        second = session.draft_pack.concepts[1].concept_id
        apply_action(session, session.reviewer, ReviewAction(
            action_type="set_status",
            target=second,
            payload={"status": "provisional"},
            rationale="Keep provisional pending further review.",
        ))

    if session.draft_pack.conflicts:
        apply_action(session, session.reviewer, ReviewAction(
            action_type="resolve_conflict",
            target="",
            payload={"conflict": session.draft_pack.conflicts[0]},
            rationale="Resolved first conflict in demo workflow.",
        ))

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    export_review_state_json(session, outdir / "review_session.json")
    export_review_ui_data(session, outdir)
    write_review_ui(outdir)

    if config.review.write_promoted_pack:
        export_promoted_pack(session, outdir / "promoted_pack")

    print("== Didactopus Review Workflow ==")
    print(f"Draft pack: {args.draft_pack}")
    print(f"Reviewer: {session.reviewer}")
    print(f"Concepts: {len(session.draft_pack.concepts)}")
    print(f"Ledger entries: {len(session.ledger)}")
    print(f"Remaining conflicts: {len(session.draft_pack.conflicts)}")
    print(f"Output dir: {outdir}")
