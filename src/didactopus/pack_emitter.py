from __future__ import annotations

from pathlib import Path
import json
import yaml
from .course_schema import NormalizedCourse, ConceptCandidate, DraftPack


def build_source_corpus(course: NormalizedCourse) -> dict:
    fragments = []
    for module in course.modules:
        for lesson in module.lessons:
            body = lesson.body.strip()
            if body:
                fragments.append(
                    {
                        "fragment_id": f"{module.title}::{lesson.title}::body".lower().replace(" ", "-"),
                        "kind": "lesson_body",
                        "module_title": module.title,
                        "lesson_title": lesson.title,
                        "text": body,
                        "source_refs": list(lesson.source_refs),
                        "objectives": list(lesson.objectives),
                        "exercises": list(lesson.exercises),
                        "key_terms": list(lesson.key_terms),
                    }
                )
            for idx, objective in enumerate(lesson.objectives, start=1):
                fragments.append(
                    {
                        "fragment_id": f"{module.title}::{lesson.title}::objective-{idx}".lower().replace(" ", "-"),
                        "kind": "objective",
                        "module_title": module.title,
                        "lesson_title": lesson.title,
                        "text": objective,
                        "source_refs": list(lesson.source_refs),
                    }
                )
            for idx, exercise in enumerate(lesson.exercises, start=1):
                fragments.append(
                    {
                        "fragment_id": f"{module.title}::{lesson.title}::exercise-{idx}".lower().replace(" ", "-"),
                        "kind": "exercise",
                        "module_title": module.title,
                        "lesson_title": lesson.title,
                        "text": exercise,
                        "source_refs": list(lesson.source_refs),
                    }
                )

    return {
        "course_title": course.title,
        "rights_note": course.rights_note,
        "sources": [
            {
                "source_path": src.source_path,
                "source_type": src.source_type,
                "title": src.title,
                "metadata": getattr(src, "metadata", {}),
            }
            for src in course.source_records
        ],
        "fragments": fragments,
    }


def build_draft_pack(
    course: NormalizedCourse,
    concepts: list[ConceptCandidate],
    author: str,
    license_name: str,
    review_flags: list[str],
    conflicts: list[str] | None = None,
) -> DraftPack:
    pack_name = course.title.lower().replace(" ", "-")
    pack = {
        "name": pack_name,
        "display_name": course.title,
        "version": "0.1.0-draft",
        "schema_version": "1",
        "didactopus_min_version": "0.1.0",
        "didactopus_max_version": "0.9.99",
        "description": f"Draft topic pack generated from multi-course inputs for '{course.title}'.",
        "author": author,
        "license": license_name,
        "dependencies": [],
        "overrides": [],
        "profile_templates": {},
        "cross_pack_links": [],
        "supporting_artifacts": ["source_corpus.json"],
    }
    concepts_yaml = {
        "concepts": [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "prerequisites": c.prerequisites,
                "mastery_signals": c.mastery_signals,
                "mastery_profile": {},
            }
            for c in concepts
        ]
    }
    roadmap = {
        "stages": [
            {
                "id": f"stage-{i+1}",
                "title": module.title,
                "concepts": [c.id for c in concepts if module.title in c.source_modules and c.title in c.source_lessons],
                "checkpoint": [ex for lesson in module.lessons for ex in lesson.exercises[:2]],
            }
            for i, module in enumerate(course.modules)
        ]
    }
    project_items = []
    for module in course.modules:
        for lesson in module.lessons:
            text = f"{lesson.title}\n{lesson.body}".lower()
            if "project" in text or "capstone" in text:
                project_items.append({
                    "id": lesson.title.lower().replace(" ", "-"),
                    "title": lesson.title,
                    "difficulty": "review-required",
                    "prerequisites": [],
                    "deliverables": ["project artifact"],
                })
    projects = {"projects": project_items}
    rubrics = {"rubrics": [{"id": "draft-rubric", "title": "Draft Rubric", "criteria": ["correctness", "explanation"]}]}
    attribution = {
        "rights_note": course.rights_note,
        "sources": [
            {"source_path": src.source_path, "source_type": src.source_type, "title": src.title}
            for src in course.source_records
        ],
    }
    return DraftPack(
        pack=pack,
        concepts=concepts_yaml,
        roadmap=roadmap,
        projects=projects,
        rubrics=rubrics,
        review_report=review_flags,
        attribution=attribution,
        conflicts=conflicts or [],
    )


def write_draft_pack(pack: DraftPack, outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack.yaml").write_text(yaml.safe_dump(pack.pack, sort_keys=False), encoding="utf-8")
    (out / "concepts.yaml").write_text(yaml.safe_dump(pack.concepts, sort_keys=False), encoding="utf-8")
    (out / "roadmap.yaml").write_text(yaml.safe_dump(pack.roadmap, sort_keys=False), encoding="utf-8")
    (out / "projects.yaml").write_text(yaml.safe_dump(pack.projects, sort_keys=False), encoding="utf-8")
    (out / "rubrics.yaml").write_text(yaml.safe_dump(pack.rubrics, sort_keys=False), encoding="utf-8")
    review_lines = ["# Review Report", ""] + [f"- {flag}" for flag in pack.review_report] if pack.review_report else ["# Review Report", "", "- none"]
    (out / "review_report.md").write_text("\n".join(review_lines), encoding="utf-8")
    conflict_lines = ["# Conflict Report", ""] + [f"- {flag}" for flag in pack.conflicts] if pack.conflicts else ["# Conflict Report", "", "- none"]
    (out / "conflict_report.md").write_text("\n".join(conflict_lines), encoding="utf-8")
    (out / "license_attribution.json").write_text(json.dumps(pack.attribution, indent=2), encoding="utf-8")


def write_source_corpus(course: NormalizedCourse, outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_corpus.json").write_text(json.dumps(build_source_corpus(course), indent=2), encoding="utf-8")
