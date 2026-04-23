from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifact_registry import validate_pack
from .document_adapters import adapt_documents
from .knowledge_graph import write_knowledge_graph
from .pack_emitter import build_draft_pack, write_draft_pack, write_source_corpus
from .rule_policy import RuleContext, build_default_rules, run_rules
from .topic_ingest import build_topic_bundle, document_to_course, extract_concept_candidates, merge_courses_into_topic_course


def run_doclift_bundle_demo(
    bundle_dir: str | Path,
    course_title: str,
    pack_dir: str | Path,
    author: str = "doclift bundle import",
    license_name: str = "See source bundle metadata",
) -> dict:
    bundle_dir = Path(bundle_dir)
    pack_dir = Path(pack_dir)

    docs = adapt_documents(bundle_dir)
    if not docs:
        raise ValueError(f"No documents found in doclift bundle {bundle_dir}")

    courses = [document_to_course(doc, course_title) for doc in docs]
    merged = merge_courses_into_topic_course(build_topic_bundle(course_title, courses))
    concepts = extract_concept_candidates(merged)
    lesson_concept_ids = {concept.id for concept in concepts if concept.title in {lesson.title for module in merged.modules for lesson in module.lessons}}
    concepts = [concept for concept in concepts if concept.id in lesson_concept_ids]
    ctx = RuleContext(course=merged, concepts=concepts)
    run_rules(ctx, build_default_rules(enable_projects=False, enable_review=False))

    draft = build_draft_pack(
        merged,
        ctx.concepts,
        author=author,
        license_name=license_name,
        review_flags=ctx.review_flags,
        conflicts=[],
    )
    write_draft_pack(draft, pack_dir)
    write_source_corpus(merged, pack_dir)
    write_knowledge_graph(merged, ctx.concepts, pack_dir)

    validation = validate_pack(pack_dir)
    if not validation.is_valid:
        raise ValueError(f"Generated pack failed validation: {validation.errors}")

    summary = {
        "bundle_dir": str(bundle_dir),
        "course_title": course_title,
        "pack_dir": str(pack_dir),
        "source_document_count": len(docs),
        "module_count": len(merged.modules),
        "concept_count": len(ctx.concepts),
        "review_flags": list(ctx.review_flags),
    }
    (pack_dir / "doclift_bundle_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Didactopus draft pack from a doclift bundle.")
    parser.add_argument("bundle_dir")
    parser.add_argument("pack_dir")
    parser.add_argument("--course-title", required=True)
    parser.add_argument("--author", default="doclift bundle import")
    parser.add_argument("--license-name", default="See source bundle metadata")
    args = parser.parse_args()

    summary = run_doclift_bundle_demo(
        bundle_dir=args.bundle_dir,
        course_title=args.course_title,
        pack_dir=args.pack_dir,
        author=args.author,
        license_name=args.license_name,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
