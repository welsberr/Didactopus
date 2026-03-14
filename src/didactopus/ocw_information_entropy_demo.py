from __future__ import annotations

import json
from pathlib import Path

from .agentic_loop import AgenticStudentState, integrate_attempt
from .artifact_registry import validate_pack
from .document_adapters import adapt_document
from .evaluator_pipeline import LearnerAttempt
from .graph_builder import build_concept_graph
from .mastery_ledger import (
    build_capability_profile,
    export_artifact_manifest,
    export_capability_profile_json,
    export_capability_report_markdown,
)
from .pack_emitter import build_draft_pack, write_draft_pack
from .rule_policy import RuleContext, build_default_rules, run_rules
from .topic_ingest import build_topic_bundle, document_to_course, extract_concept_candidates, merge_courses_into_topic_course

DEFAULT_RIGHTS_NOTE = (
    "Derived from MIT OpenCourseWare 6.050J Information and Entropy (Spring 2008). "
    "Retain MIT OCW attribution and applicable Creative Commons terms before redistribution."
)

DEFAULT_SKILL_TEMPLATE = """---
name: ocw-information-entropy-agent
description: Use the generated MIT OCW Information and Entropy pack, concept ordering, and learner artifacts to mentor or evaluate information-theory work.
---

# OCW Information Entropy Agent

Use this skill when the task is about tutoring, evaluating, or planning study in Information Theory using the generated MIT OCW 6.050J pack.

## Workflow

1. Read `references/generated-course-summary.md` for the pack structure and target concepts.
2. Read `references/generated-capability-summary.md` to understand what the demo AI learner already mastered.
3. Use `assets/generated/pack/` as the source of truth for concept ids, prerequisites, and mastery signals.
4. When giving guidance, preserve the pack ordering from fundamentals through coding and thermodynamics.
5. When uncertain, say which concept or prerequisite in the generated pack is underspecified.

## Outputs

- study plans grounded in the pack prerequisites
- concept explanations tied to entropy, coding, and channel capacity
- evaluation checklists using the generated capability report
- follow-up exercises that extend the existing learner artifacts
"""


def _strong_attempt(concept_key: str, title: str) -> LearnerAttempt:
    symbolic_terms = ("coding", "capacity", "information")
    artifact_type = "symbolic" if any(term in concept_key for term in symbolic_terms) else "explanation"
    content = (
        f"{title} matters because it links uncertainty to communication. "
        f"Therefore {title.lower()} = structure for reasoning about messages. "
        "One assumption is an idealized source model, one limitation is finite data, "
        "and uncertainty remains when observations are noisy."
    )
    return LearnerAttempt(
        concept=concept_key,
        artifact_type=artifact_type,
        content=content,
        metadata={"deliverable_count": 2, "artifact_name": f"{concept_key.split('::')[-1]}.md"},
    )


def _write_skill_bundle(
    skill_dir: Path,
    pack_dir: Path,
    run_dir: Path,
    concept_path: list[str],
    mastered_concepts: list[str],
) -> None:
    references_dir = skill_dir / "references"
    assets_dir = skill_dir / "assets" / "generated"
    references_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "agents").mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(DEFAULT_SKILL_TEMPLATE, encoding="utf-8")
    (skill_dir / "agents" / "openai.yaml").write_text(
        "\n".join(
            [
                "display_name: OCW Information Entropy Agent",
                "short_description: Tutor and assess with the generated MIT OCW information-theory pack.",
                "default_prompt: Help me use the MIT OCW information-and-entropy pack to study or evaluate work.",
            ]
        ),
        encoding="utf-8",
    )

    summary_lines = [
        "# Generated Course Summary",
        "",
        f"- Pack dir: `{pack_dir}`",
        f"- Run dir: `{run_dir}`",
        "",
        "## Curriculum Path Used By The Demo Learner",
    ]
    summary_lines.extend(f"- {concept}" for concept in concept_path)
    summary_lines.extend(["", "## Mastered Concepts"])
    summary_lines.extend(f"- {concept}" for concept in mastered_concepts)
    (references_dir / "generated-course-summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    capability_report = run_dir / "capability_report.md"
    capability_summary = capability_report.read_text(encoding="utf-8") if capability_report.exists() else "# Capability Report\n"
    (references_dir / "generated-capability-summary.md").write_text(capability_summary, encoding="utf-8")

    pack_asset_dir = assets_dir / "pack"
    run_asset_dir = assets_dir / "run"
    pack_asset_dir.mkdir(parents=True, exist_ok=True)
    run_asset_dir.mkdir(parents=True, exist_ok=True)

    for source in pack_dir.iterdir():
        if source.is_file():
            (pack_asset_dir / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    for source in run_dir.iterdir():
        if source.is_file():
            (run_asset_dir / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def run_ocw_information_entropy_demo(
    course_source: str | Path,
    pack_dir: str | Path,
    run_dir: str | Path,
    skill_dir: str | Path,
) -> dict:
    course_source = Path(course_source)
    pack_dir = Path(pack_dir)
    run_dir = Path(run_dir)
    skill_dir = Path(skill_dir)

    doc = adapt_document(course_source)
    course = document_to_course(doc, "MIT OCW Information and Entropy")
    merged = merge_courses_into_topic_course(build_topic_bundle(course.title, [course]))
    merged.rights_note = DEFAULT_RIGHTS_NOTE

    concepts = extract_concept_candidates(merged)
    ctx = RuleContext(course=merged, concepts=concepts)
    run_rules(ctx, build_default_rules())

    draft = build_draft_pack(
        merged,
        ctx.concepts,
        author="MIT OCW derived demo",
        license_name="CC BY-NC-SA 4.0",
        review_flags=ctx.review_flags,
        conflicts=[],
    )
    write_draft_pack(draft, pack_dir)

    validation = validate_pack(pack_dir)
    if not validation.is_valid:
        raise ValueError(f"Generated pack failed validation: {validation.errors}")

    graph = build_concept_graph([validation], default_dimension_thresholds={
        "correctness": 0.8,
        "explanation": 0.75,
        "transfer": 0.7,
        "project_execution": 0.75,
        "critique": 0.7,
    })
    target_key = f"{draft.pack['name']}::thermodynamics-and-entropy"
    concept_path = graph.curriculum_path_to_target(set(), target_key)

    state = AgenticStudentState(
        learner_id="ocw-information-entropy-agent",
        display_name="OCW Information Entropy Agent",
    )
    for concept_key in concept_path:
        title = graph.graph.nodes[concept_key].get("title", concept_key.split("::")[-1])
        integrate_attempt(state, _strong_attempt(concept_key, title))

    profile = build_capability_profile(state, merged.title)
    run_dir.mkdir(parents=True, exist_ok=True)
    export_capability_profile_json(profile, str(run_dir / "capability_profile.json"))
    export_capability_report_markdown(profile, str(run_dir / "capability_report.md"))
    export_artifact_manifest(profile, str(run_dir / "artifact_manifest.json"))

    summary = {
        "course_source": str(course_source),
        "pack_dir": str(pack_dir),
        "skill_dir": str(skill_dir),
        "review_flags": list(ctx.review_flags),
        "concept_count": len(ctx.concepts),
        "target_concept": target_key,
        "curriculum_path": concept_path,
        "mastered_concepts": sorted(state.mastered_concepts),
        "artifact_count": len(state.artifacts),
    }
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _write_skill_bundle(skill_dir, pack_dir, run_dir, concept_path, summary["mastered_concepts"])
    return summary


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a domain pack and skill bundle from MIT OCW Information and Entropy.")
    parser.add_argument(
        "--course-source",
        default=str(root / "examples" / "ocw-information-entropy" / "6-050j-information-and-entropy.md"),
    )
    parser.add_argument(
        "--pack-dir",
        default=str(root / "domain-packs" / "mit-ocw-information-entropy"),
    )
    parser.add_argument(
        "--run-dir",
        default=str(root / "examples" / "ocw-information-entropy-run"),
    )
    parser.add_argument(
        "--skill-dir",
        default=str(root / "skills" / "ocw-information-entropy-agent"),
    )
    args = parser.parse_args()

    summary = run_ocw_information_entropy_demo(
        course_source=args.course_source,
        pack_dir=args.pack_dir,
        run_dir=args.run_dir,
        skill_dir=args.skill_dir,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
