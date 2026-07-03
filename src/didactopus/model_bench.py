from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from epistemap import (
    g_evaluation_row,
    g_experiment_manifest,
    g_experiment_summary,
    write_g_experiment_manifest,
    write_g_rows_csv,
)

from .config import load_config
from .language_support import language_alignment_score, response_language_instruction
from .learner_session import _grounding_block
from .model_provider import ModelProvider
from .multilingual_qa import multilingual_qa_for_text, round_trip_source_phrases, round_trip_warning_for_phrases
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


def _multilingual_score(role: str, text: str, language: str, qa_spec: dict | None = None) -> tuple[float, list[str]]:
    score, notes = language_alignment_score(text, language)
    if language == "en":
        return score, notes
    qa_score = 1.0
    qa_notes: list[str] = []
    if qa_spec:
        qa_result = multilingual_qa_for_text(qa_spec, language=language, text=text)
        qa_notes = list(qa_result["warnings"])
        summary = qa_result["summary"]
        denominator = summary["required_term_count"] + summary["required_caveat_count"] + summary["forbidden_confusion_count"]
        numerator = summary["matched_term_count"] + summary["matched_caveat_count"] + (
            summary["forbidden_confusion_count"] - summary["confusion_hit_count"]
        )
        if denominator > 0:
            qa_score = max(0.0, min(1.0, numerator / denominator))
    role_lower = role.lower()
    if role_lower == "mentor" and "entropy" not in text.lower():
        qa_notes = list(qa_notes)
        qa_notes.append("Did not visibly preserve a key grounded concept term in multilingual output.")
        qa_score = max(0.0, qa_score - 0.2)
    combined = (score * 0.5) + (qa_score * 0.5)
    return combined, [*notes, *qa_notes]


def _round_trip_phrases(qa_spec: dict | None, language: str) -> list[str]:
    if not qa_spec or language == "en":
        return []
    return round_trip_source_phrases(qa_spec, language=language)[:6]


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


def model_benchmark_g_evaluation_rows(payload: dict) -> list[dict]:
    """Return canonical G rows for model-benchmark adequacy evaluation."""

    benchmark = payload.get("benchmark", {})
    context = payload.get("context", {})
    hardware = benchmark.get("hardware_profile", {})
    if not isinstance(hardware, dict):
        hardware = {}
    rows = []
    for result in payload.get("role_results", []):
        role = result["role"]
        rows.append(
            g_evaluation_row(
                y=1 if result["adequacy_rating"] == "adequate" else 0,
                p=float(result["adequacy_score"]),
                env=str(result.get("env", "K")),
                run_id=str(benchmark.get("name", "didactopus-local-model-adequacy")),
                subject_id=str(result.get("model_name", "")),
                condition=str(hardware.get("profile_name", "")),
                phase=role,
                item_id=f"{context.get('output_language', 'en')}::{role}",
                claim_id=f"didactopus-model-benchmark::{role}::adequate-grounded-behavior",
                answer=str(result["adequacy_rating"]),
                response=str(result.get("response_preview", "")),
                source_anchor=str(context.get("skill_name", "")),
                metadata={
                    "provider": result.get("provider", ""),
                    "language": context.get("output_language", ""),
                    "hardware_cpu": hardware.get("cpu", ""),
                    "hardware_ram_gb": hardware.get("ram_gb", ""),
                    "latency_ms": result.get("latency_ms", ""),
                    "grounded_score": result.get("grounded_score", ""),
                    "multilingual_score": result.get("multilingual_score", ""),
                    "evaluation_target": "grounded_role_behavior",
                },
            )
        )
    return rows


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
                    system_prompt=system_prompt_for_role(role),
                    temperature=0.0,
                    max_tokens=220,
                ).text
                round_trip = round_trip_warning_for_phrases(source_phrases, back_translation)
        adequacy_scores.append(combined_score)
        role_results.append(
            {
                "role": role,
                "provider": response.provider,
                "model_name": response.model_name,
                "latency_ms": elapsed_ms,
                "response_preview": response.text[:280],
                "adequacy_score": round(combined_score, 3),
                "adequacy_rating": _adequacy_rating(combined_score),
                "grounded_score": round(score, 3),
                "multilingual_score": round(multilingual_score, 3),
                "round_trip": round_trip,
                "notes": [*notes, *multilingual_notes, *round_trip["warnings"]],
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
    rows = model_benchmark_g_evaluation_rows(payload)
    write_g_rows_csv(rows, out_dir / "model_benchmark_g_rows.csv")
    manifest = g_experiment_manifest(
        experiment_id="didactopus-local-model-adequacy",
        name="Didactopus local-model adequacy benchmark",
        row_file="model_benchmark_g_rows.csv",
        evaluation_target="grounded_role_behavior",
        corpus=str(payload["context"]["skill_name"]),
        conditions=[payload["benchmark"]["hardware_profile"]["profile_name"]],
        phases=["mentor", "practice", "evaluator"],
        reliability_treatment="single-model-local-hardware-profile",
        temporal_assumptions={"clock": "role_sequence"},
        row_count=len(rows),
        metadata={
            "provider": payload["benchmark"]["provider"],
            "output_language": payload["context"]["output_language"],
        },
    )
    write_g_experiment_manifest(
        manifest,
        out_dir / "model_benchmark_g_manifest.json",
    )
    (out_dir / "model_benchmark_g_summary.json").write_text(
        json.dumps(g_experiment_summary(rows, manifest=manifest, group_by="condition"), indent=2),
        encoding="utf-8",
    )

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
