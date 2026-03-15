from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from .evaluator_pipeline import CritiqueEvaluator, LearnerAttempt, RubricEvaluator, SymbolicRuleEvaluator, aggregate, run_pipeline


@dataclass
class SkillContext:
    skill_name: str
    skill_description: str
    course_summary: str
    capability_summary: str
    pack: dict
    concepts: list[dict]
    capability_profile: dict
    run_summary: dict


def load_ocw_skill_context(skill_dir: str | Path) -> SkillContext:
    skill_dir = Path(skill_dir)
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    skill_name = "ocw-information-entropy-agent"
    skill_description = ""
    lines = skill_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "---":
            continue
        if line.startswith("name:"):
            skill_name = line.split(":", 1)[1].strip()
        if line.startswith("description:"):
            skill_description = line.split(":", 1)[1].strip()
        if idx > 10 and skill_description:
            break

    pack_dir = skill_dir / "assets" / "generated" / "pack"
    run_dir = skill_dir / "assets" / "generated" / "run"
    return SkillContext(
        skill_name=skill_name,
        skill_description=skill_description,
        course_summary=(skill_dir / "references" / "generated-course-summary.md").read_text(encoding="utf-8"),
        capability_summary=(skill_dir / "references" / "generated-capability-summary.md").read_text(encoding="utf-8"),
        pack=yaml.safe_load((pack_dir / "pack.yaml").read_text(encoding="utf-8")) or {},
        concepts=(yaml.safe_load((pack_dir / "concepts.yaml").read_text(encoding="utf-8")) or {}).get("concepts", []),
        capability_profile=json.loads((run_dir / "capability_profile.json").read_text(encoding="utf-8")),
        run_summary=json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8")),
    )


def _concept_key(pack_name: str, concept_id: str) -> str:
    return f"{pack_name}::{concept_id}"


def _match_concepts(context: SkillContext, task: str, limit: int = 3) -> list[dict]:
    task_lower = task.lower()
    scored = []
    for concept in context.concepts:
        text = " ".join(
            [
                str(concept.get("id", "")),
                str(concept.get("title", "")),
                str(concept.get("description", "")),
            ]
        ).lower()
        score = sum(1 for token in task_lower.split() if token in text)
        if score:
            scored.append((score, concept))
    scored.sort(key=lambda item: (item[0], len(item[1].get("prerequisites", []))), reverse=True)
    return [concept for _, concept in scored[:limit]]


def build_skill_grounded_study_plan(context: SkillContext, target_task: str) -> dict:
    pack_name = context.pack.get("name", "mit-ocw-information-and-entropy")
    matched = _match_concepts(context, target_task)
    if not matched:
        matched = [c for c in context.concepts if c.get("id") in {"shannon-entropy", "channel-capacity", "thermodynamics-and-entropy"}]

    steps = []
    for concept in matched:
        concept_id = concept["id"]
        concept_key = _concept_key(pack_name, concept_id)
        steps.append(
            {
                "concept_key": concept_key,
                "title": concept["title"],
                "status": "mastered" if concept_key in context.capability_profile.get("mastered_concepts", []) else "review-needed",
                "prerequisites": [
                    _concept_key(pack_name, prereq) for prereq in concept.get("prerequisites", [])
                ],
                "recommended_action": (
                    f"Use {concept['title']} as the primary teaching anchor."
                    if concept_key in context.capability_profile.get("mastered_concepts", [])
                    else f"Review prerequisites before teaching {concept['title']}."
                ),
            }
        )

    return {
        "skill": context.skill_name,
        "task": target_task,
        "steps": steps,
        "guided_path_reference": list(context.run_summary.get("curriculum_path", [])),
    }


def build_skill_grounded_explanation(context: SkillContext, concept_id: str) -> dict:
    pack_name = context.pack.get("name", "mit-ocw-information-and-entropy")
    concept = next((item for item in context.concepts if item.get("id") == concept_id), None)
    if concept is None:
        raise KeyError(f"Unknown concept id: {concept_id}")

    concept_key = _concept_key(pack_name, concept_id)
    summary = context.capability_profile.get("evaluator_summary_by_concept", {}).get(concept_key, {})
    explanation = (
        f"{concept['title']} is represented in the Information and Entropy skill as part of a progression from "
        f"foundational probability ideas toward communication limits and physical interpretation. "
        f"It depends on {', '.join(concept.get('prerequisites', []) or ['no explicit prerequisites in the generated pack'])}. "
        f"The current demo learner already mastered this concept, with evaluator means {summary}, so the skill can use it as a stable explanation anchor."
    )
    return {
        "concept_key": concept_key,
        "title": concept["title"],
        "explanation": explanation,
        "source_description": concept.get("description", ""),
    }


def evaluate_submission_with_skill(context: SkillContext, concept_id: str, submission: str) -> dict:
    pack_name = context.pack.get("name", "mit-ocw-information-and-entropy")
    concept_key = _concept_key(pack_name, concept_id)
    attempt = LearnerAttempt(
        concept=concept_key,
        artifact_type="symbolic",
        content=submission,
        metadata={"skill_name": context.skill_name},
    )
    results = run_pipeline(attempt, [RubricEvaluator(), SymbolicRuleEvaluator(), CritiqueEvaluator()])
    aggregated = aggregate(results)
    mastered_reference = concept_key in context.capability_profile.get("mastered_concepts", [])
    verdict = "acceptable" if aggregated.get("correctness", 0.0) >= 0.75 and aggregated.get("explanation", 0.0) >= 0.75 else "needs_revision"
    return {
        "concept_key": concept_key,
        "submission": submission,
        "verdict": verdict,
        "aggregated": aggregated,
        "evaluators": [
            {"name": result.evaluator_name, "dimensions": result.dimensions, "notes": result.notes}
            for result in results
        ],
        "skill_reference": {
            "skill_name": context.skill_name,
            "mastered_by_demo_agent": mastered_reference,
        },
        "follow_up": (
            "Extend the answer with an explicit limitation or assumption."
            if verdict == "acceptable"
            else "Rework the answer so it states the equality/relationship explicitly and explains why it matters."
        ),
    }


def run_ocw_skill_agent_demo(skill_dir: str | Path, out_dir: str | Path) -> dict:
    context = load_ocw_skill_context(skill_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    study_plan = build_skill_grounded_study_plan(
        context,
        "Help a learner connect Shannon entropy, channel capacity, and thermodynamic entropy.",
    )
    explanation = build_skill_grounded_explanation(context, "channel-capacity")
    evaluation = evaluate_submission_with_skill(
        context,
        "thermodynamics-and-entropy",
        "Therefore entropy = uncertainty in a message model, but one limitation is that thermodynamic entropy and Shannon entropy are not identical without careful interpretation.",
    )

    payload = {
        "skill": {
            "name": context.skill_name,
            "description": context.skill_description,
        },
        "study_plan": study_plan,
        "explanation": explanation,
        "evaluation": evaluation,
    }
    (out_dir / "skill_demo.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# OCW Information and Entropy Skill Demo",
        "",
        f"- Skill: `{context.skill_name}`",
        f"- Description: {context.skill_description}",
        "",
        "## Study Plan",
    ]
    for step in study_plan["steps"]:
        lines.append(f"- {step['title']} ({step['status']}): {step['recommended_action']}")
    lines.extend(
        [
            "",
            "## Explanation Demo",
            explanation["explanation"],
            "",
            "## Evaluation Demo",
            f"- Verdict: {evaluation['verdict']}",
            f"- Aggregated dimensions: {evaluation['aggregated']}",
            f"- Follow-up: {evaluation['follow_up']}",
        ]
    )
    (out_dir / "skill_demo.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Show an agentic system using the Information and Entropy knowledge export as a skill.")
    parser.add_argument(
        "--skill-dir",
        default=str(root / "skills" / "ocw-information-entropy-agent"),
    )
    parser.add_argument(
        "--out-dir",
        default=str(root / "examples" / "ocw-information-entropy-skill-demo"),
    )
    args = parser.parse_args()
    payload = run_ocw_skill_agent_demo(args.skill_dir, args.out_dir)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
