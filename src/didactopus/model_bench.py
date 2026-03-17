from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from .config import load_config
from .language_support import response_language_instruction
from .learner_session import _grounding_block
from .model_provider import ModelProvider
from .ocw_skill_agent_demo import build_skill_grounded_study_plan, evaluate_submission_with_skill, load_ocw_skill_context
from .role_prompts import system_prompt_for_role


def _score_mentor_response(text: str) -> tuple[float, list[str]]:
    lowered = text.lower()
    score = 0.0
    notes: list[str] = []
    if "concept" in lowered or "entropy" in lowered:
        score += 0.35
    else:
        notes.append("Did not clearly reference the grounded concept.")
    if "?" in text:
        score += 0.35
    else:
        notes.append("Did not ask a focused learner question.")
    if "supporting lessons" in lowered or "prerequisite" in lowered or "course notes" in lowered:
        score += 0.3
    else:
        notes.append("Did not clearly surface grounded structure or prerequisites.")
    return min(score, 1.0), notes


def _score_practice_response(text: str) -> tuple[float, list[str]]:
    lowered = text.lower()
    score = 0.0
    notes: list[str] = []
    if "practice" in lowered or "task" in lowered or "compare" in lowered or "explain" in lowered:
        score += 0.35
    else:
        notes.append("Did not clearly frame an exercise.")
    if "solution" not in lowered and "answer:" not in lowered:
        score += 0.35
    else:
        notes.append("Looks too close to giving away the full solution.")
    if "entropy" in lowered or "concept" in lowered or "channel" in lowered:
        score += 0.3
    else:
        notes.append("Did not stay visibly tied to the grounded topic.")
    return min(score, 1.0), notes


def _score_evaluator_response(text: str) -> tuple[float, list[str]]:
    lowered = text.lower()
    score = 0.0
    notes: list[str] = []
    if "strength" in lowered or "correct" in lowered or "good" in lowered:
        score += 0.35
    else:
        notes.append("Did not acknowledge learner strengths.")
    if "not identical" in lowered or "limitation" in lowered or "careful" in lowered:
        score += 0.35
    else:
        notes.append("Did not preserve the learner's existing caveat.")
    if "next" in lowered or "revise" in lowered or "follow-up" in lowered or "improve" in lowered:
        score += 0.3
    else:
        notes.append("Did not provide a concrete next step.")
    return min(score, 1.0), notes


def _adequacy_rating(score: float) -> str:
    if score >= 0.8:
        return "adequate"
    if score >= 0.6:
        return "borderline"
    return "inadequate"


def _hardware_profile(
    *,
    profile_name: str,
    cpu: str,
    ram_gb: float | None,
    notes: str | None,
) -> dict:
    return {
        "profile_name": profile_name,
        "cpu": cpu,
        "ram_gb": ram_gb,
        "notes": notes or "",
    }


def run_model_benchmark(
    *,
    config_path: str | Path,
    skill_dir: str | Path,
    out_dir: str | Path,
    hardware_profile_name: str = "unspecified-local",
    hardware_cpu: str = "unknown",
    hardware_ram_gb: float | None = None,
    hardware_notes: str | None = None,
    language: str = "en",
) -> dict:
    config = load_config(config_path)
    provider = ModelProvider(config.model_provider)
    context = load_ocw_skill_context(skill_dir)
    study_plan = build_skill_grounded_study_plan(
        context,
        "Help a learner connect Shannon entropy, channel capacity, and thermodynamic entropy.",
    )
    steps = study_plan.get("steps", [])
    if len(steps) < 2:
        raise ValueError("Benchmark requires at least two grounded study-plan steps.")

    primary = steps[0]
    secondary = steps[1]
    learner_submission = (
        "Entropy measures uncertainty because more possible outcomes require more information to describe, "
        "but thermodynamic entropy is not identical to Shannon entropy without careful interpretation."
    )
    deterministic = evaluate_submission_with_skill(
        context,
        primary["concept_key"].split("::", 1)[-1],
        learner_submission,
    )

    prompts = {
        "mentor": (
            f"{_grounding_block(primary)}\n\n"
            f"{_grounding_block(secondary)}\n\n"
            "Give a grounded mentor response that orients the learner, explains the sequence, and asks one focused question."
        ),
        "practice": (
            f"{_grounding_block(primary)}\n\n"
            "Create one reasoning-heavy practice task. Keep it grounded and do not provide the full solution."
        ),
        "evaluator": (
            f"{_grounding_block(primary)}\n\n"
            f"Learner submission: {learner_submission}\n"
            f"Deterministic evaluator result: verdict={deterministic['verdict']}, aggregated={deterministic['aggregated']}\n"
            "Respond as evaluator. Acknowledge what the learner already did correctly, preserve existing caveats, and give one next revision target."
        ),
    }

    scorers = {
        "mentor": _score_mentor_response,
        "practice": _score_practice_response,
        "evaluator": _score_evaluator_response,
    }

    role_results = []
    adequacy_scores = []
    for role, prompt in prompts.items():
        started = perf_counter()
        response = provider.generate(
            f"{prompt}{response_language_instruction(language, 'en')}",
            role=role,
            system_prompt=system_prompt_for_role(role),
            temperature=0.2,
            max_tokens=220,
        )
        elapsed_ms = round((perf_counter() - started) * 1000.0, 3)
        score, notes = scorers[role](response.text)
        adequacy_scores.append(score)
        role_results.append(
            {
                "role": role,
                "provider": response.provider,
                "model_name": response.model_name,
                "latency_ms": elapsed_ms,
                "response_preview": response.text[:280],
                "adequacy_score": round(score, 3),
                "adequacy_rating": _adequacy_rating(score),
                "notes": notes,
            }
        )

    overall_score = sum(adequacy_scores) / len(adequacy_scores)
    payload = {
        "benchmark": {
            "name": "didactopus-local-model-adequacy",
            "task_family": "graph-grounded-mentor-loop",
            "provider": config.model_provider.provider,
            "hardware_profile": _hardware_profile(
                profile_name=hardware_profile_name,
                cpu=hardware_cpu,
                ram_gb=hardware_ram_gb,
                notes=hardware_notes,
            ),
        },
        "context": {
            "skill_name": context.skill_name,
            "study_plan_task": study_plan["task"],
            "primary_concept": primary["title"],
            "secondary_concept": secondary["title"],
            "source_language": "en",
            "output_language": language,
        },
        "role_results": role_results,
        "summary": {
            "overall_adequacy_score": round(overall_score, 3),
            "overall_adequacy_rating": _adequacy_rating(overall_score),
            "recommended_use": (
                "Suitable for local guided-learning experiments."
                if overall_score >= 0.8
                else "Use with caution; responses should stay in review."
                if overall_score >= 0.6
                else "Not recommended for learner-facing local deployment."
            ),
        },
    }

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "model_benchmark.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Didactopus Local Model Benchmark",
        "",
        f"- Provider: `{payload['benchmark']['provider']}`",
        f"- Hardware profile: `{payload['benchmark']['hardware_profile']['profile_name']}`",
        f"- Primary concept: {payload['context']['primary_concept']}",
        f"- Secondary concept: {payload['context']['secondary_concept']}",
        f"- Overall adequacy: {payload['summary']['overall_adequacy_rating']} ({payload['summary']['overall_adequacy_score']})",
        f"- Recommended use: {payload['summary']['recommended_use']}",
        "",
        "## Role Results",
    ]
    for result in role_results:
        lines.append(
            f"- `{result['role']}` via `{result['model_name']}`: "
            f"{result['adequacy_rating']} ({result['adequacy_score']}), latency {result['latency_ms']} ms"
        )
        if result["notes"]:
            lines.append(f"  Notes: {'; '.join(result['notes'])}")
    (out_dir / "model_benchmark.md").write_text("\n".join(lines), encoding="utf-8")

    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Benchmark local-model adequacy for the Didactopus mentor loop.")
    parser.add_argument("--config", default=str(root / "configs" / "config.example.yaml"))
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out-dir", default=str(root / "examples" / "model-benchmark"))
    parser.add_argument("--hardware-profile", default="unspecified-local")
    parser.add_argument("--hardware-cpu", default="unknown")
    parser.add_argument("--hardware-ram-gb", type=float, default=None)
    parser.add_argument("--hardware-notes", default="")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    payload = run_model_benchmark(
        config_path=args.config,
        skill_dir=args.skill_dir,
        out_dir=args.out_dir,
        hardware_profile_name=args.hardware_profile,
        hardware_cpu=args.hardware_cpu,
        hardware_ram_gb=args.hardware_ram_gb,
        hardware_notes=args.hardware_notes,
        language=args.language,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
