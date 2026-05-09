from __future__ import annotations

import json
from pathlib import Path
import sys
import re

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


def _stage_groundrecall_pack_source(pack_dir: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in ["pack.yaml", "concepts.yaml", "roadmap.yaml", "projects.yaml", "rubrics.yaml"]:
        source = pack_dir / name
        if source.exists():
            target = target_dir / name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target_dir


def _select_target_concept(pack_name: str, concepts: list, preferred_id: str = "thermodynamics-and-entropy") -> str:
    ids = [concept.id for concept in concepts]
    if preferred_id in ids:
        return f"{pack_name}::{preferred_id}"
    if not ids:
        raise ValueError("No concept candidates available to select as target.")
    return f"{pack_name}::{ids[-1]}"


def _pack_concept_ref(target_key: str, concepts: list) -> str:
    target_id = target_key.split("::", 1)[-1]
    for concept in concepts:
        if concept.id == target_id:
            return concept.title
    return target_id


def _load_groundrecall_runtime():
    groundrecall_src = Path("/home/netuser/bin/GroundRecall/src")
    if groundrecall_src.exists():
        sys.path.insert(0, str(groundrecall_src))
    from groundrecall import export_groundrecall_query_bundle, promote_import_to_store, run_groundrecall_import  # type: ignore

    return run_groundrecall_import, promote_import_to_store, export_groundrecall_query_bundle


def _merge_source_inventories(primary_path: Path, extra_path: Path, out_path: Path) -> Path:
    primary = load_sources(primary_path)
    extra = load_sources(extra_path)
    merged = []
    seen_ids: set[str] = set()
    for source in [*primary.sources, *extra.sources]:
        if source.source_id in seen_ids:
            continue
        seen_ids.add(source.source_id)
        merged.append(source.model_dump())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    out_path.write_text(yaml.safe_dump({"sources": merged}, sort_keys=False), encoding="utf-8")
    return out_path


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "untitled"


def _merge_concept_descriptions(primary: str, secondary: str, max_chars: int = 640) -> str:
    primary = (primary or "").strip()
    secondary = (secondary or "").strip()
    if not primary:
        return secondary[:max_chars]
    if not secondary or secondary in primary:
        return primary[:max_chars]
    merged = f"{primary} {secondary}".strip()
    return merged[:max_chars]


def _merge_unique(existing: list[str], additions: list[str]) -> list[str]:
    seen = set(existing)
    out = list(existing)
    for item in additions:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _load_wolfe_concept_alignment(wolfe_snippets_dir: Path | None) -> dict[str, str]:
    if wolfe_snippets_dir is None:
        return {}
    import yaml

    path = wolfe_snippets_dir / "concept-alignment.yaml"
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    alignments = payload.get("alignments", []) or []
    mapping: dict[str, str] = {}
    for item in alignments:
        if not isinstance(item, dict):
            continue
        source_title = str(item.get("source_title", "")).strip()
        target_title = str(item.get("target_title", "")).strip()
        if source_title and target_title:
            mapping[source_title] = target_title
    return mapping


def _apply_concept_alignment(concepts: list, alignment: dict[str, str]) -> list:
    if not alignment:
        return concepts
    merged_by_id: dict[str, object] = {}
    ordered_ids: list[str] = []
    for concept in concepts:
        target_title = alignment.get(concept.title, concept.title)
        target_id = _slugify(target_title)
        if target_id not in merged_by_id:
            concept.id = target_id
            concept.title = target_title
            merged_by_id[target_id] = concept
            ordered_ids.append(target_id)
            continue
        existing = merged_by_id[target_id]
        existing.description = _merge_concept_descriptions(existing.description, concept.description)
        existing.source_modules = _merge_unique(existing.source_modules, concept.source_modules)
        existing.source_lessons = _merge_unique(existing.source_lessons, concept.source_lessons)
        existing.source_courses = _merge_unique(existing.source_courses, concept.source_courses)
        existing.prerequisites = _merge_unique(existing.prerequisites, concept.prerequisites)
        existing.mastery_signals = _merge_unique(existing.mastery_signals, concept.mastery_signals)
        existing.distinctions = _merge_unique(existing.distinctions, concept.distinctions)
        existing.definition_candidates = _merge_unique(existing.definition_candidates, concept.definition_candidates)
        existing.qualification_candidates = _merge_unique(existing.qualification_candidates, concept.qualification_candidates)
        existing.constraint_candidates = _merge_unique(existing.constraint_candidates, concept.constraint_candidates)
        if existing.source_role != "nuance" and concept.source_role == "nuance":
            existing.source_role = concept.source_role
    return [merged_by_id[item] for item in ordered_ids]


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
    wolfe_snippets_dir: str | Path | None = None,
    wolfe_source_inventory: str | Path | None = None,
) -> dict:
    course_source = Path(course_source)
    source_inventory = Path(source_inventory)
    pack_dir = Path(pack_dir)
    run_dir = Path(run_dir)
    skill_dir = Path(skill_dir)
    wolfe_snippets_dir = Path(wolfe_snippets_dir) if wolfe_snippets_dir is not None else None
    wolfe_source_inventory = Path(wolfe_source_inventory) if wolfe_source_inventory is not None else None

    docs = adapt_documents(course_source)
    wolfe_doc_count = 0
    if wolfe_snippets_dir is not None and wolfe_snippets_dir.exists():
        wolfe_docs = [
            doc
            for doc in adapt_documents(wolfe_snippets_dir)
            if Path(getattr(doc, "source_path", "")).name not in {"concept-alignment.yaml", "concept-alignment.yml", "concept-alignment.json"}
        ]
        docs.extend(wolfe_docs)
        wolfe_doc_count = len(wolfe_docs)
    if wolfe_doc_count and not (wolfe_source_inventory is not None and wolfe_source_inventory.exists()):
        review_flag = (
            "Wolfe snippet augmentation was used without a Wolfe source inventory; compliance manifest excludes those augmentation sources."
        )
    else:
        review_flag = ""
    if not docs:
        raise ValueError(f"No supported source documents found under {course_source}")
    courses = [document_to_course(doc, "MIT OCW Information and Entropy") for doc in docs]
    merged = merge_courses_into_topic_course(build_topic_bundle("MIT OCW Information and Entropy", courses))
    merged.rights_note = DEFAULT_RIGHTS_NOTE

    concepts = extract_concept_candidates(merged)
    concepts = _apply_concept_alignment(concepts, _load_wolfe_concept_alignment(wolfe_snippets_dir))
    ctx = RuleContext(course=merged, concepts=concepts)
    run_rules(ctx, build_default_rules())
    if review_flag:
        ctx.review_flags.append(review_flag)

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
    effective_inventory_path = source_inventory
    if wolfe_source_inventory is not None and wolfe_source_inventory.exists():
        effective_inventory_path = _merge_source_inventories(
            source_inventory,
            wolfe_source_inventory,
            run_dir / "merged_source_inventory.yaml",
        )
    if effective_inventory_path.exists():
        inventory = load_sources(effective_inventory_path)
        compliance_manifest = build_pack_compliance_manifest(draft.pack["name"], draft.pack["display_name"], inventory)
        write_manifest(compliance_manifest, pack_dir / "pack_compliance_manifest.json")
        if effective_inventory_path.suffix.lower() in {".yaml", ".yml"}:
            (pack_dir / "source_inventory.yaml").write_text(effective_inventory_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            (pack_dir / "source_inventory.json").write_text(effective_inventory_path.read_text(encoding="utf-8"), encoding="utf-8")

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
    target_concept_ref = _pack_concept_ref(target_key, ctx.concepts)
    concept_path = graph.curriculum_path_to_target(set(), target_key)

    run_groundrecall_import, promote_import_to_store, export_groundrecall_query_bundle = _load_groundrecall_runtime()
    groundrecall_root = run_dir / "groundrecall"
    groundrecall_source_pack = _stage_groundrecall_pack_source(pack_dir, groundrecall_root / "pack-source")
    import_result = run_groundrecall_import(
        groundrecall_source_pack,
        out_root=groundrecall_root / "imports",
        mode="quick",
        import_id="didactopus-pack",
    )
    store_dir = groundrecall_root / "store"
    promote_import_to_store(
        import_result.out_dir,
        store_dir,
        reviewer="Didactopus OCW demo",
        allow_lint_errors=True,
    )
    exported_bundle = export_groundrecall_query_bundle(
        store_dir,
        target_concept_ref,
        groundrecall_root / "export",
    )

    draft = build_draft_pack(
        merged,
        ctx.concepts,
        author="MIT OCW derived demo",
        license_name="CC BY-NC-SA 4.0",
        review_flags=ctx.review_flags,
        conflicts=[],
        groundrecall_query_bundle=exported_bundle["bundle"],
    )
    write_draft_pack(draft, pack_dir)

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
        "effective_source_inventory": str(effective_inventory_path),
        "wolfe_snippets_dir": str(wolfe_snippets_dir) if wolfe_snippets_dir is not None else "",
        "wolfe_source_inventory": str(wolfe_source_inventory) if wolfe_source_inventory is not None else "",
        "wolfe_source_document_count": wolfe_doc_count,
        "review_flags": list(ctx.review_flags),
        "concept_count": len(ctx.concepts),
        "source_fragment_count": len(json.loads((pack_dir / "source_corpus.json").read_text(encoding="utf-8")).get("fragments", [])),
        "knowledge_graph_summary": json.loads((pack_dir / "knowledge_graph.json").read_text(encoding="utf-8")).get("summary", {}),
        "target_concept": target_key,
        "groundrecall_concept_ref": target_concept_ref,
        "groundrecall_bundle_included": (pack_dir / "groundrecall_query_bundle.json").exists(),
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
    parser.add_argument("--wolfe-snippets-dir")
    parser.add_argument("--wolfe-source-inventory")
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
        wolfe_snippets_dir=args.wolfe_snippets_dir,
        wolfe_source_inventory=args.wolfe_source_inventory,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
