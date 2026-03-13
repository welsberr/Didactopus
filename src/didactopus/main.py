from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .document_adapters import adapt_document
from .topic_ingest import document_to_course, build_topic_bundle, merge_courses_into_topic_course, extract_concept_candidates
from .cross_course_conflicts import detect_title_overlaps, detect_term_conflicts, detect_order_conflicts, detect_thin_concepts
from .rule_policy import RuleContext, build_default_rules, run_rules
from .pack_emitter import build_draft_pack, write_draft_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus document-adapter and cross-course topic ingestion")
    parser.add_argument("--inputs", nargs="+", required=True, help="Document inputs")
    parser.add_argument("--title", required=True, help="Topic title")
    parser.add_argument("--rights-note", default="REVIEW REQUIRED")
    parser.add_argument("--output-dir", default="generated-topic-pack")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    docs = [adapt_document(path) for path in args.inputs]
    courses = [document_to_course(doc, course_title=args.title) for doc in docs]
    topic = build_topic_bundle(args.title, courses)
    merged_course = merge_courses_into_topic_course(
        topic_bundle=topic,
        merge_same_named_lessons=config.cross_course.merge_same_named_lessons,
    )
    concepts = extract_concept_candidates(merged_course)

    context = RuleContext(course=merged_course, concepts=concepts)
    rules = build_default_rules()
    run_rules(context, rules)

    conflicts = []
    if config.cross_course.detect_title_overlaps:
        conflicts.extend(detect_title_overlaps(merged_course))
    if config.cross_course.detect_term_conflicts:
        conflicts.extend(detect_term_conflicts(merged_course))
    if config.cross_course.detect_order_conflicts:
        conflicts.extend(detect_order_conflicts(merged_course))
    conflicts.extend(detect_thin_concepts(context.concepts))

    draft = build_draft_pack(
        course=merged_course,
        concepts=context.concepts,
        author=config.course_ingest.default_pack_author,
        license_name=config.course_ingest.default_license,
        review_flags=context.review_flags,
        conflicts=conflicts,
    )
    write_draft_pack(draft, args.output_dir)

    print("== Didactopus Cross-Course Topic Ingest ==")
    print(f"Topic: {args.title}")
    print(f"Documents: {len(docs)}")
    print(f"Courses: {len(courses)}")
    print(f"Merged modules: {len(merged_course.modules)}")
    print(f"Concept candidates: {len(context.concepts)}")
    print(f"Review flags: {len(context.review_flags)}")
    print(f"Conflicts: {len(conflicts)}")
    print(f"Output dir: {args.output_dir}")


if __name__ == "__main__":
    main()
