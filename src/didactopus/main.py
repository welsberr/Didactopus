from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .course_ingest import parse_source_file, merge_source_records, extract_concept_candidates
from .rule_policy import RuleContext, build_default_rules, run_rules
from .conflict_report import detect_duplicate_lessons, detect_term_conflicts, detect_thin_concepts
from .pack_emitter import build_draft_pack, write_draft_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus multi-source course-to-pack ingestion pipeline")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input source files")
    parser.add_argument("--title", required=True, help="Course or topic title")
    parser.add_argument("--rights-note", default="REVIEW REQUIRED")
    parser.add_argument("--output-dir", default="generated-pack")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    records = [parse_source_file(path, title=args.title) for path in args.inputs]
    course = merge_source_records(
        records=records,
        course_title=args.title,
        rights_note=args.rights_note,
        merge_same_named_lessons=config.multisource.merge_same_named_lessons,
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

    conflicts = []
    if config.multisource.detect_duplicate_lessons:
        conflicts.extend(detect_duplicate_lessons(course))
    if config.multisource.detect_term_conflicts:
        conflicts.extend(detect_term_conflicts(course))
    conflicts.extend(detect_thin_concepts(context.concepts))

    draft = build_draft_pack(
        course=course,
        concepts=context.concepts,
        author=config.course_ingest.default_pack_author,
        license_name=config.course_ingest.default_license,
        review_flags=context.review_flags,
        conflicts=conflicts,
    )
    write_draft_pack(draft, args.output_dir)

    print("== Didactopus Multi-Source Course Ingest ==")
    print(f"Course: {course.title}")
    print(f"Sources: {len(records)}")
    print(f"Modules: {len(course.modules)}")
    print(f"Concept candidates: {len(context.concepts)}")
    print(f"Review flags: {len(context.review_flags)}")
    print(f"Conflicts: {len(conflicts)}")
    print(f"Output dir: {args.output_dir}")


if __name__ == "__main__":
    main()
