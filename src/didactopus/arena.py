from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import yaml

from .config import load_config
from .language_support import response_language_instruction
from .learner_session import _grounding_block
from .model_bench import _adequacy_rating, _score_evaluator_response, _score_mentor_response, _score_practice_response
from .model_provider import ModelProvider
from .ocw_skill_agent_demo import build_skill_grounded_study_plan, evaluate_submission_with_skill, load_ocw_skill_context
from .role_prompts import system_prompt_for_role_variant


def _default_arena_spec() -> dict:
    return {
        "candidates": [
            {"name": "stub-baseline", "config": "configs/config.example.yaml", "prompt_variant": "baseline", "language": "en"},
            {"name": "stub-strict-grounding", "config": "configs/config.example.yaml", "prompt_variant": "strict_grounding", "language": "en"},
            {"name": "stub-trust-preserving", "config": "configs/config.example.yaml", "prompt_variant": "trust_preserving", "language": "en"},
        ],
        "review": {
            "enabled": True,
            "config": "configs/config.example.yaml",
            "role": "mentor",
        },
    }


def load_arena_spec(path: str | Path | None) -> dict:
    if path is None:
        return _default_arena_spec()
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if "candidates" not in data:
        data["candidates"] = _default_arena_spec()["candidates"]
    return data


def _arena_tasks(context) -> tuple[list[dict], str, dict]:
    study_plan = build_skill_grounded_study_plan(
        context,
        "Help a learner connect Shannon entropy, channel capacity, and thermodynamic entropy.",
    )
    steps = study_plan.get("steps", [])
    if len(steps) < 2:
        raise ValueError("Arena requires at least two grounded study-plan steps.")
    learner_submission = (
        "Entropy measures uncertainty because more possible outcomes require more information to describe, "
        "but thermodynamic entropy is not identical to Shannon entropy without careful interpretation."
    )
    deterministic = evaluate_submission_with_skill(
        context,
        steps[0]["concept_key"].split("::", 1)[-1],
        learner_submission,
    )
    return steps[:2], learner_submission, deterministic


def _arena_role_prompts(primary: dict, secondary: dict, learner_submission: str, deterministic: dict) -> dict[str, str]:
    return {
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


def _scorer_for_role(role: str):
    return {
        "mentor": _score_mentor_response,
        "practice": _score_practice_response,
        "evaluator": _score_evaluator_response,
    }[role]


def _run_candidate(candidate: dict, skill_dir: str | Path) -> dict:
    config = load_config(candidate["config"])
    provider = ModelProvider(config.model_provider)
    context = load_ocw_skill_context(skill_dir)
    steps, learner_submission, deterministic = _arena_tasks(context)
    primary, secondary = steps
    prompts = _arena_role_prompts(primary, secondary, learner_submission, deterministic)
    variant = candidate.get("prompt_variant", "baseline")
    language = candidate.get("language", "en")

    role_results = []
    overall = 0.0
    for role, prompt in prompts.items():
        started = perf_counter()
        response = provider.generate(
            f"{prompt}{response_language_instruction(language, 'en')}",
            role=role,
            system_prompt=system_prompt_for_role_variant(role, variant),
            temperature=0.2,
            max_tokens=220,
        )
        elapsed_ms = round((perf_counter() - started) * 1000.0, 3)
        score, notes = _scorer_for_role(role)(response.text)
        overall += score
        role_results.append(
            {
                "role": role,
                "provider": response.provider,
                "model_name": response.model_name,
                "prompt_variant": variant,
                "language": language,
                "latency_ms": elapsed_ms,
                "adequacy_score": round(score, 3),
                "adequacy_rating": _adequacy_rating(score),
                "response_preview": response.text[:280],
                "notes": notes,
            }
        )

    overall /= len(role_results)
    return {
        "candidate_name": candidate["name"],
        "config": candidate["config"],
        "prompt_variant": variant,
        "language": language,
        "provider": config.model_provider.provider,
        "overall_score": round(overall, 3),
        "overall_rating": _adequacy_rating(overall),
        "role_results": role_results,
    }


def _build_review_queue(candidate_results: list[dict]) -> list[dict]:
    queue = []
    for result in candidate_results:
        weak_roles = [item["role"] for item in result["role_results"] if item["adequacy_rating"] != "adequate"]
        queue.append(
            {
                "candidate_name": result["candidate_name"],
                "overall_rating": result["overall_rating"],
                "overall_score": result["overall_score"],
                "needs_human_review": result["overall_rating"] != "adequate" or bool(weak_roles),
                "weak_roles": weak_roles,
            }
        )
    return queue


def _llm_review_summary(candidate_results: list[dict], spec: dict) -> dict | None:
    review_spec = spec.get("review", {})
    if not review_spec.get("enabled", False):
        return None
    config = load_config(review_spec.get("config", "configs/config.example.yaml"))
    provider = ModelProvider(config.model_provider)
    ranked = sorted(candidate_results, key=lambda item: item["overall_score"], reverse=True)
    summary_lines = []
    for result in ranked[:3]:
        summary_lines.append(
            f"- {result['candidate_name']}: overall {result['overall_rating']} ({result['overall_score']}), "
            f"language={result['language']}, roles={[(item['role'], item['adequacy_rating'], item['adequacy_score']) for item in result['role_results']]}"
        )
    prompt = "\n".join(
        [
            "Review these Didactopus arena results for a human reviewer.",
            "Rank the strongest candidates, identify likely prompt improvements, and state uncertainty clearly.",
            "Do not claim that any candidate is fully validated. Treat this as initial review support only.",
            "",
            "Arena results:",
            *summary_lines,
        ]
    )
    role = review_spec.get("role", "mentor")
    response = provider.generate(
        prompt,
        role=role,
        system_prompt=system_prompt_for_role_variant(role, "trust_preserving"),
        temperature=0.2,
        max_tokens=260,
    )
    return {
        "provider": response.provider,
        "model_name": response.model_name,
        "role": role,
        "summary": response.text,
    }


def run_didactopus_arena(
    *,
    arena_spec_path: str | Path | None,
    skill_dir: str | Path,
    out_dir: str | Path,
) -> dict:
    spec = load_arena_spec(arena_spec_path)
    candidate_results = [_run_candidate(candidate, skill_dir) for candidate in spec.get("candidates", [])]
    ranked = sorted(candidate_results, key=lambda item: item["overall_score"], reverse=True)
    payload = {
        "arena": {
            "name": "didactopus-behavior-arena",
            "candidate_count": len(candidate_results),
        },
        "ranked_candidates": ranked,
        "review_queue": _build_review_queue(ranked),
        "llm_review": _llm_review_summary(ranked, spec),
    }

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "arena_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "arena_review_queue.json").write_text(json.dumps(payload["review_queue"], indent=2), encoding="utf-8")

    lines = [
        "# Didactopus Arena Report",
        "",
        f"- Candidates: {payload['arena']['candidate_count']}",
        "",
        "## Rankings",
    ]
    for result in ranked:
        lines.append(
            f"- `{result['candidate_name']}` via `{result['provider']}` / prompt variant `{result['prompt_variant']}`: "
            f"{result['overall_rating']} ({result['overall_score']}), language `{result['language']}`"
        )
    lines.extend(["", "## Human Review Queue"])
    for item in payload["review_queue"]:
        lines.append(
            f"- `{item['candidate_name']}`: needs_human_review={item['needs_human_review']}, weak_roles={item['weak_roles']}"
        )
    if payload["llm_review"] is not None:
        lines.extend(["", "## LLM Review Summary", payload["llm_review"]["summary"]])
    (out_dir / "arena_report.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run the Didactopus model-and-prompt arena.")
    parser.add_argument("--arena-spec", default=None)
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out-dir", default=str(root / "examples" / "arena"))
    args = parser.parse_args()
    payload = run_didactopus_arena(
        arena_spec_path=args.arena_spec,
        skill_dir=args.skill_dir,
        out_dir=args.out_dir,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
