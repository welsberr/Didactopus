from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import yaml
from epistemap import (
    g_evaluation_row,
    g_experiment_manifest,
    g_experiment_summary,
    write_g_experiment_summary_markdown,
    write_g_experiment_manifest,
    write_g_rows_csv,
)

from .config import load_config
from .language_support import response_language_instruction
from .learner_session import _grounding_block
from .model_bench import (
    _adequacy_rating,
    _multilingual_score,
    _round_trip_phrases,
    _score_evaluator_response,
    _score_mentor_response,
    _score_practice_response,
)
from .model_provider import ModelProvider
from .multilingual_qa import round_trip_warning_for_phrases
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
        multilingual_score, multilingual_notes = _multilingual_score(role, response.text, language, context.multilingual_qa)
        combined_score = (score * 0.8) + (multilingual_score * 0.2)
        round_trip = {"warnings": [], "summary": {"source_phrase_count": 0, "round_trip_warning_count": 0, "drifted_phrases": []}}
        if language != "en":
            source_phrases = _round_trip_phrases(context.multilingual_qa, language)
            if source_phrases:
                back_translation = provider.generate(
                    (
                        "Translate the following text into English as faithfully as possible, preserving technical meaning and caveats.\n\n"
                        f"{response.text}"
                    ),
                    role=role,
                    system_prompt=system_prompt_for_role_variant(role, variant),
                    temperature=0.0,
                    max_tokens=220,
                ).text
                round_trip = round_trip_warning_for_phrases(source_phrases, back_translation)
        overall += combined_score
        role_results.append(
            {
                "role": role,
                "provider": response.provider,
                "model_name": response.model_name,
                "prompt_variant": variant,
                "language": language,
                "latency_ms": elapsed_ms,
                "adequacy_score": round(combined_score, 3),
                "adequacy_rating": _adequacy_rating(combined_score),
                "grounded_score": round(score, 3),
                "multilingual_score": round(multilingual_score, 3),
                "round_trip": round_trip,
                "response_preview": response.text[:280],
                "notes": [*notes, *multilingual_notes, *round_trip["warnings"]],
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


def arena_g_evaluation_rows(candidate_results: list[dict]) -> list[dict]:
    """Return canonical G rows for arena adequacy evaluation.

    These rows evaluate grounded role behavior, not source-claim truth.
    """

    rows = []
    for result in candidate_results:
        for role_result in result["role_results"]:
            role = role_result["role"]
            rows.append(
                g_evaluation_row(
                    y=1 if role_result["adequacy_rating"] == "adequate" else 0,
                    p=float(role_result["adequacy_score"]),
                    env=str(role_result.get("env", result.get("env", "K"))),
                    run_id="didactopus-behavior-arena",
                    subject_id=result["candidate_name"],
                    condition=result["prompt_variant"],
                    phase=role,
                    item_id=f"{result['language']}::{role}",
                    claim_id=f"didactopus-arena::{role}::adequate-grounded-behavior",
                    answer=role_result["adequacy_rating"],
                    response=role_result.get("response_preview", ""),
                    source_anchor=result.get("config", ""),
                    metadata={
                        "provider": result.get("provider", ""),
                        "model_name": role_result.get("model_name", ""),
                        "language": result.get("language", ""),
                        "latency_ms": role_result.get("latency_ms", ""),
                        "grounded_score": role_result.get("grounded_score", ""),
                        "multilingual_score": role_result.get("multilingual_score", ""),
                        "evaluation_target": "grounded_role_behavior",
                    },
                )
            )
    return rows


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
    rows = arena_g_evaluation_rows(ranked)
    write_g_rows_csv(rows, out_dir / "arena_g_rows.csv")
    manifest = g_experiment_manifest(
        experiment_id="didactopus-behavior-arena",
        name="Didactopus behavior arena",
        row_file="arena_g_rows.csv",
        evaluation_target="grounded_role_behavior",
        corpus="ocw-information-entropy-agent",
        conditions=sorted({result["prompt_variant"] for result in ranked}),
        phases=["mentor", "practice", "evaluator"],
        reliability_treatment="prompt-variant-comparison",
        temporal_assumptions={"clock": "role_sequence"},
        row_count=len(rows),
        metadata={"candidate_count": len(ranked)},
    )
    write_g_experiment_manifest(
        manifest,
        out_dir / "arena_g_manifest.json",
    )
    g_summary = g_experiment_summary(rows, manifest=manifest, group_by="condition")
    (out_dir / "arena_g_summary.json").write_text(json.dumps(g_summary, indent=2), encoding="utf-8")
    write_g_experiment_summary_markdown(g_summary, out_dir / "arena_g_summary.md")

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
