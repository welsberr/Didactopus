from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .course_ingest import parse_markdown_course, extract_concept_candidates
from .rule_policy import RuleContext, build_default_rules, run_rules
from .pack_emitter import build_draft_pack, write_draft_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus course-to-pack ingestion pipeline")
    parser.add_argument("--input", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--source-name", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--rights-note", default="REVIEW REQUIRED")
    parser.add_argument("--output-dir", default="generated-pack")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    text = Path(args.input).read_text(encoding="utf-8")

    course = parse_markdown_course(
        text=text,
        title=args.title,
        source_name=args.source_name,
        source_url=args.source_url,
        rights_note=args.rights_note,
    )
    concepts = extract_concept_candidates(course)
    context = RuleContext(course=course, concepts=concepts)

    rules = build_default_rules(
        enable_prereq=config.rule_policy.enable_prerequisite_order_rule,
        enable_merge=config.rule_policy.enable_duplicate_term_merge_rule,
        enable_projects=config.rule_policy.enable_project_detection_rule,
        enable_review=config.rule_policy.enable_review_flags,
    )
    run_rules(context, rules)

    draft = build_draft_pack(
        course=course,
        concepts=context.concepts,
        author=config.course_ingest.default_pack_author,
        license_name=config.course_ingest.default_license,
        review_flags=context.review_flags,
    )
    write_draft_pack(draft, args.output_dir)

    print("== Didactopus Course-to-Pack Ingest ==")
    print(f"Course: {course.title}")
    print(f"Modules: {len(course.modules)}")
    print(f"Concept candidates: {len(context.concepts)}")
    print(f"Review flags: {len(context.review_flags)}")
    print(f"Output dir: {args.output_dir}")


if __name__ == "__main__":
    main()
