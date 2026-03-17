from __future__ import annotations

import json
from pathlib import Path

from .agentic_loop import AgenticStudentState, integrate_attempt
from .artifact_registry import validate_pack
from .course_ingestion_compliance import build_pack_compliance_manifest, load_sources, write_manifest
from .course_repo import bootstrap_course_repo, resolve_course_repo
from .document_adapters import adapt_documents
from .evaluator_pipeline import LearnerAttempt
from .graph_builder import build_concept_graph
from .mastery_ledger import (
    build_capability_profile,
    export_artifact_manifest,
    export_capability_profile_json,
    export_capability_report_markdown,
)
from .knowledge_graph import write_knowledge_graph
from .pack_emitter import build_draft_pack, write_draft_pack, write_source_corpus
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
2. Read `references/generated-capability-summary.md` to understand what the deterministic demo learner already mastered.
3. Use `assets/generated/pack/` as the source of truth for concept ids, prerequisites, and mastery signals.
4. Use `assets/generated/pack/source_corpus.json` to ground explanations in the ingested source material before relying on model prior knowledge.
5. When giving guidance, preserve the pack ordering from fundamentals through coding and thermodynamics.
6. When uncertain, say which concept or prerequisite in the generated pack is underspecified and which source fragment would need review.

## Outputs

- study plans grounded in the pack prerequisites
- concept explanations tied to entropy, coding, and channel capacity
- evaluation checklists using the generated capability report
- follow-up exercises that extend the existing learner artifacts
- local-LLM tutoring or evaluation runs that use the same pack and source corpus through role-based prompts
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


def _select_target_concept(pack_name: str, concepts: list, preferred_id: str = "thermodynamics-and-entropy") -> str:
    ids = [concept.id for concept in concepts]
    if preferred_id in ids:
        return f"{pack_name}::{preferred_id}"
    if not ids:
        raise ValueError("No concept candidates available to select as target.")
    return f"{pack_name}::{ids[-1]}"


def resolve_ocw_demo_paths(
    root: Path,
    course_repo: str | Path | None = None,
    course_source: str | Path | None = None,
    source_inventory: str | Path | None = None,
    pack_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    skill_dir: str | Path | None = None,
) -> dict[str, str]:
    if course_repo is not None:
        repo = resolve_course_repo(course_repo)
        return {
            "course_source": str(Path(course_source) if course_source is not None else Path(repo.source_dir)),
            "source_inventory": str(Path(source_inventory) if source_inventory is not None else Path(repo.source_inventory)),
            "pack_dir": str(Path(pack_dir) if pack_dir is not None else Path(repo.generated_pack_dir or (root / "domain-packs" / repo.course_id))),
            "run_dir": str(Path(run_dir) if run_dir is not None else Path(repo.generated_run_dir or (root / "examples" / f"{repo.course_id}-run"))),
            "skill_dir": str(Path(skill_dir) if skill_dir is not None else Path(repo.generated_skill_dir or (root / "skills" / f"{repo.course_id}-agent"))),
        }
    return {
        "course_source": str(Path(course_source) if course_source is not None else root / "examples" / "ocw-information-entropy" / "course"),
        "source_inventory": str(Path(source_inventory) if source_inventory is not None else root / "examples" / "ocw-information-entropy" / "sources.yaml"),
        "pack_dir": str(Path(pack_dir) if pack_dir is not None else root / "domain-packs" / "mit-ocw-information-entropy"),
        "run_dir": str(Path(run_dir) if run_dir is not None else root / "examples" / "ocw-information-entropy-run"),
        "skill_dir": str(Path(skill_dir) if skill_dir is not None else root / "skills" / "ocw-information-entropy-agent"),
    }


def bootstrap_ocw_course_repo_target(
    target_dir: str | Path,
    root: Path,
    course_source: str | Path | None = None,
    source_inventory: str | Path | None = None,
) -> dict[str, str]:
    source_path = Path(course_source) if course_source is not None else root / "examples" / "ocw-information-entropy" / "course"
    inventory_path = Path(source_inventory) if source_inventory is not None else root / "examples" / "ocw-information-entropy" / "sources.yaml"
    resolved = bootstrap_course_repo(
        target_dir=target_dir,
        course_id="mit-ocw-information-entropy",
        display_name="MIT OCW Information and Entropy",
        course_source=source_path,
        source_inventory=inventory_path,
        license_family="CC BY-NC-SA 4.0",
    )
    return {
        "course_source": resolved.source_dir,
        "source_inventory": resolved.source_inventory,
        "pack_dir": resolved.generated_pack_dir or str(Path(resolved.repo_root) / "generated" / "pack"),
        "run_dir": resolved.generated_run_dir or str(Path(resolved.repo_root) / "generated" / "run"),
        "skill_dir": resolved.generated_skill_dir or str(Path(resolved.repo_root) / "generated" / "skill"),
    }


def run_ocw_information_entropy_demo(
    course_source: str | Path,
    source_inventory: str | Path,
    pack_dir: str | Path,
    run_dir: str | Path,
    skill_dir: str | Path,
) -> dict:
    course_source = Path(course_source)
    source_inventory = Path(source_inventory)
    pack_dir = Path(pack_dir)
    run_dir = Path(run_dir)
    skill_dir = Path(skill_dir)

    docs = adapt_documents(course_source)
    if not docs:
        raise ValueError(f"No supported source documents found under {course_source}")
    courses = [document_to_course(doc, "MIT OCW Information and Entropy") for doc in docs]
    merged = merge_courses_into_topic_course(build_topic_bundle("MIT OCW Information and Entropy", courses))
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
    write_source_corpus(merged, pack_dir)
    write_knowledge_graph(merged, ctx.concepts, pack_dir)
    if source_inventory.exists():
        inventory = load_sources(source_inventory)
        compliance_manifest = build_pack_compliance_manifest(draft.pack["name"], draft.pack["display_name"], inventory)
        write_manifest(compliance_manifest, pack_dir / "pack_compliance_manifest.json")
        (pack_dir / "source_inventory.yaml").write_text(source_inventory.read_text(encoding="utf-8"), encoding="utf-8")

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
    target_key = _select_target_concept(draft.pack["name"], ctx.concepts)
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
        "source_document_count": len(docs),
        "pack_dir": str(pack_dir),
        "skill_dir": str(skill_dir),
        "source_inventory": str(source_inventory),
        "review_flags": list(ctx.review_flags),
        "concept_count": len(ctx.concepts),
        "source_fragment_count": len(json.loads((pack_dir / "source_corpus.json").read_text(encoding="utf-8")).get("fragments", [])),
        "knowledge_graph_summary": json.loads((pack_dir / "knowledge_graph.json").read_text(encoding="utf-8")).get("summary", {}),
        "target_concept": target_key,
        "curriculum_path": concept_path,
        "mastered_concepts": sorted(state.mastered_concepts),
        "artifact_count": len(state.artifacts),
    }
    compliance_path = pack_dir / "pack_compliance_manifest.json"
    if compliance_path.exists():
        summary["compliance_manifest"] = str(compliance_path)
        summary["compliance"] = json.loads(compliance_path.read_text(encoding="utf-8"))
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _write_skill_bundle(skill_dir, pack_dir, run_dir, concept_path, summary["mastered_concepts"])
    return summary


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a domain pack and skill bundle from MIT OCW Information and Entropy.")
    parser.add_argument("--course-repo")
    parser.add_argument("--course-repo-target")
    parser.add_argument("--course-source")
    parser.add_argument("--source-inventory")
    parser.add_argument("--pack-dir")
    parser.add_argument("--run-dir")
    parser.add_argument("--skill-dir")
    args = parser.parse_args()

    if args.course_repo_target:
        resolved = bootstrap_ocw_course_repo_target(
            target_dir=args.course_repo_target,
            root=root,
            course_source=args.course_source,
            source_inventory=args.source_inventory,
        )
    else:
        resolved = resolve_ocw_demo_paths(
            root,
            course_repo=args.course_repo,
            course_source=args.course_source,
            source_inventory=args.source_inventory,
            pack_dir=args.pack_dir,
            run_dir=args.run_dir,
            skill_dir=args.skill_dir,
        )

    summary = run_ocw_information_entropy_demo(
        course_source=resolved["course_source"],
        source_inventory=resolved["source_inventory"],
        pack_dir=resolved["pack_dir"],
        run_dir=resolved["run_dir"],
        skill_dir=resolved["skill_dir"],
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
