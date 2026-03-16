from __future__ import annotations

import json
from pathlib import Path
import sys

from .config import load_config
from .model_provider import ModelProvider
from .ocw_skill_agent_demo import load_ocw_skill_context
from .role_prompts import evaluator_system_prompt, learner_system_prompt, mentor_system_prompt, practice_system_prompt


def _format_turn(role: str, speaker: str, content: str) -> dict[str, str]:
    return {"role": role, "speaker": speaker, "content": content.strip()}


def _normalize_completion(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped
    if _looks_truncated(stripped):
        return stripped.rstrip(" ,;:-") + "."
    return stripped


def _looks_truncated(text: str) -> bool:
    def _ends_with_truncated_marker(line: str) -> bool:
        lowered_line = line.lower()
        return any(lowered_line.endswith(marker) for marker in truncated_markers)

    stripped = text.strip()
    if not stripped:
        return True
    if stripped.endswith(("...", "…")):
        return True
    truncated_markers = (
        "for example,",
        "for instance,",
        "such as",
        "this means",
        "therefore",
        "however",
        "furthermore",
        "in particular",
        "suppose we have",
        "which means",
        "so the",
        "is h =",
        "compare the entropy of one roll with the",
        "with a crossover",
    )
    lowered = stripped.lower()
    if _ends_with_truncated_marker(lowered):
        return True
    if stripped[-1] not in ".!?)]}\"'":
        return True
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) >= 2:
        for idx in range(len(lines) - 1):
            current = lines[idx]
            nxt = lines[idx + 1]
            if nxt[:1].isdigit():
                if _ends_with_truncated_marker(current) or current[-1] not in (".", "!", "?", ":", ")"):
                    return True
    tail = stripped.rsplit(None, 1)[-1].lower()
    return tail in {
        "a",
        "an",
        "and",
        "as",
        "because",
        "but",
        "for",
        "if",
        "in",
        "of",
        "or",
        "so",
        "the",
        "to",
        "with",
    }


def _is_topical(text: str, required_terms: list[str], forbidden_terms: list[str] | None = None) -> bool:
    lowered = text.lower()
    if forbidden_terms and any(term in lowered for term in forbidden_terms):
        return False
    return any(term in lowered for term in required_terms)


def _generate_checked(
    provider: ModelProvider,
    prompt: str,
    role: str,
    system_prompt: str,
    required_terms: list[str],
    forbidden_terms: list[str] | None = None,
    temperature: float = 0.2,
    max_tokens: int = 180,
    retries: int = 2,
    status_callback=None,
) -> str:
    attempt_prompt = prompt
    for _ in range(retries + 1):
        text = provider.generate(
            attempt_prompt,
            role=role,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            status_callback=status_callback,
        ).text
        if _is_topical(text, required_terms, forbidden_terms):
            completed = text.strip()
            continuation_budget = max(64, max_tokens // 2)
            for _continuation_idx in range(3):
                if not _looks_truncated(completed):
                    break
                continuation = provider.generate(
                    "Continue the previous response without restarting it. Finish the thought cleanly and end with a complete sentence.\n\n"
                    f"Current draft:\n{completed}",
                    role=role,
                    system_prompt=system_prompt,
                    temperature=min(temperature, 0.2),
                    max_tokens=continuation_budget,
                    status_callback=status_callback,
                ).text.strip()
                if not continuation or continuation == completed:
                    break
                completed = f"{completed.rstrip()} {continuation.lstrip()}"
                if not _looks_truncated(continuation):
                    break
            return _normalize_completion(completed)
        attempt_prompt = (
            prompt
            + " Stay strictly within information theory, entropy, probability, coding, or thermodynamics. "
            + "Do not switch to politics, programming style, or unrelated topics."
        )
    return _normalize_completion(text)


def _concept_title_map(context) -> dict[str, str]:
    return {concept.get("id", ""): concept.get("title", concept.get("id", "")) for concept in context.concepts}


def _path_titles(context, limit: int | None = None) -> list[str]:
    title_map = _concept_title_map(context)
    titles: list[str] = []
    for concept_key in context.run_summary.get("curriculum_path", []):
        concept_id = concept_key.split("::", 1)[-1]
        titles.append(title_map.get(concept_id, concept_id.replace("-", " ").title()))
    return titles[:limit] if limit is not None else titles


def _healthy_rolemesh_models(provider: ModelProvider) -> set[str]:
    config = provider.config
    if config.provider.lower() != "rolemesh":
        return set()
    models = set(config.rolemesh.role_to_model.values()) | {config.rolemesh.default_model}
    healthy: set[str] = set()
    for model in models:
        try:
            provider._rolemesh_chat_completion(  # type: ignore[attr-defined]
                {
                    "model": model,
                    "messages": [{"role": "user", "content": "Reply with ok."}],
                    "max_tokens": 16,
                    "temperature": 0.0,
                }
            )
            healthy.add(model)
        except Exception:
            continue
    return healthy


def _apply_rolemesh_fallbacks(provider: ModelProvider) -> dict[str, str]:
    config = provider.config
    if config.provider.lower() != "rolemesh":
        return {}
    healthy = _healthy_rolemesh_models(provider)
    if not healthy:
        raise RuntimeError("No healthy RoleMesh models available for transcript generation.")
    fallback_model = config.rolemesh.default_model if config.rolemesh.default_model in healthy else sorted(healthy)[0]
    adjusted = {}
    for role, model in list(config.rolemesh.role_to_model.items()):
        if model not in healthy:
            config.rolemesh.role_to_model[role] = fallback_model
            adjusted[role] = fallback_model
    return adjusted


def build_ocw_rolemesh_transcript(config_path: str | Path, skill_dir: str | Path) -> dict:
    config = load_config(config_path)
    provider = ModelProvider(config.model_provider)
    context = load_ocw_skill_context(skill_dir)
    role_fallbacks = _apply_rolemesh_fallbacks(provider)
    status_updates: list[str] = []

    def emit_status(message: str) -> None:
        status_updates.append(message)
        print(message, file=sys.stderr, flush=True)

    goal = (
        "I want to use the MIT OCW Information and Entropy course to understand how Shannon entropy, "
        "channel capacity, and thermodynamic entropy relate without skipping the reasoning."
    )
    path_titles = _path_titles(context)
    turns: list[dict[str, str]] = []
    turns.append(_format_turn("user", "Learner Goal", goal))

    mentor_open = _generate_checked(
        provider,
        "The learner wants to approach the Information and Entropy course carefully. "
        "Ask a short opening question that checks what they already understand and points them to the first concept.",
        role="mentor",
        system_prompt=mentor_system_prompt(),
        required_terms=["information", "entropy", "probability", "counting"],
        forbidden_terms=["president", "executive branch", "code"],
        temperature=0.2,
        max_tokens=140,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "Didactopus Mentor", mentor_open))

    learner_reflection = _generate_checked(
        provider,
        "Respond as the learner. Mention partial understanding of randomness and probability, but uncertainty about "
        "how that becomes entropy and communication limits in information theory.",
        role="learner",
        system_prompt=learner_system_prompt(),
        required_terms=["probability", "entropy", "information", "uncertainty"],
        forbidden_terms=["president", "executive branch", "code"],
        temperature=0.5,
        max_tokens=140,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "AI Learner", learner_reflection))

    mentor_guidance = _generate_checked(
        provider,
        "Given the learner reflection, explain the first two concepts to study from the generated path and why. "
        f"Path reference: {path_titles[:4]}",
        role="mentor",
        system_prompt=mentor_system_prompt(),
        required_terms=["counting", "probability", "entropy", "information"],
        forbidden_terms=["president", "executive branch", "code"],
        temperature=0.2,
        max_tokens=280,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "Didactopus Mentor", mentor_guidance))

    practice_task = _generate_checked(
        provider,
        "Generate one short practice task that forces the learner to connect counting/probability with Shannon entropy, "
        "without giving away the full answer.",
        role="practice",
        system_prompt=practice_system_prompt(),
        required_terms=["entropy", "probability", "die", "uncertainty", "shannon"],
        forbidden_terms=["president", "executive branch", "code"],
        temperature=0.4,
        max_tokens=220,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "Didactopus Practice Designer", practice_task))

    learner_attempt = _generate_checked(
        provider,
        f"Respond as the learner attempting this task in information theory: {practice_task} "
        "Give a concise answer in your own words, with one uncertainty still present.",
        role="learner",
        system_prompt=learner_system_prompt(),
        required_terms=["entropy", "probability", "uncertainty", "die", "message"],
        forbidden_terms=["president", "executive branch", "code"],
        temperature=0.5,
        max_tokens=280,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "AI Learner", learner_attempt))

    evaluator_feedback = _generate_checked(
        provider,
        "Evaluate this learner attempt for correctness, explanation quality, and limitations. "
        f"Task: {practice_task}\nAttempt: {learner_attempt}",
        role="evaluator",
        system_prompt=evaluator_system_prompt(),
        required_terms=["correctness", "entropy", "probability", "explanation", "limitation"],
        forbidden_terms=["president", "executive branch", "code structure"],
        temperature=0.2,
        max_tokens=260,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "Didactopus Evaluator", evaluator_feedback))

    mentor_next_step = _generate_checked(
        provider,
        "Given the evaluator feedback, tell the learner what to do next before moving on to channel capacity. "
        "Use the course path to show what comes next.",
        role="mentor",
        system_prompt=mentor_system_prompt(),
        required_terms=["channel capacity", "entropy", "probability", "next"],
        forbidden_terms=["president", "executive branch", "code structure"],
        temperature=0.2,
        max_tokens=220,
        status_callback=emit_status,
    )
    turns.append(_format_turn("assistant", "Didactopus Mentor", mentor_next_step))

    stage_specs = [
        {
            "topic": "Channel Capacity",
            "path_slice": path_titles[4:7] or path_titles,
            "practice_anchor": "binary symmetric channel",
            "required_terms": ["channel", "capacity", "entropy", "noise"],
        },
        {
            "topic": "Coding and Compression",
            "path_slice": path_titles[5:9] or path_titles,
            "practice_anchor": "compression and error-correcting code",
            "required_terms": ["coding", "compression", "redundancy", "error"],
        },
        {
            "topic": "Thermodynamic Entropy and Synthesis",
            "path_slice": path_titles[8:] or path_titles,
            "practice_anchor": "thermodynamic entropy",
            "required_terms": ["thermodynamic", "entropy", "information", "physical"],
        },
    ]

    for stage in stage_specs:
        mentor_stage = _generate_checked(
            provider,
            f"The learner is continuing through the MIT OCW Information and Entropy course. "
            f"Bridge from the previous work into {stage['topic']}. "
            f"Reference this path segment: {stage['path_slice']}. "
            "Explain what the learner should focus on before attempting a problem.",
            role="mentor",
            system_prompt=mentor_system_prompt(),
            required_terms=stage["required_terms"],
            forbidden_terms=["president", "executive branch", "code structure"],
            temperature=0.2,
            max_tokens=260,
            status_callback=emit_status,
        )
        turns.append(_format_turn("assistant", "Didactopus Mentor", mentor_stage))

        learner_stage = _generate_checked(
            provider,
            f"Respond as the learner after studying {stage['topic']}. "
            f"Summarize what now makes sense and one remaining difficulty about {stage['practice_anchor']}.",
            role="learner",
            system_prompt=learner_system_prompt(),
            required_terms=stage["required_terms"],
            forbidden_terms=["president", "executive branch", "code structure"],
            temperature=0.4,
            max_tokens=220,
            status_callback=emit_status,
        )
        turns.append(_format_turn("assistant", "AI Learner", learner_stage))

        practice_stage = _generate_checked(
            provider,
            f"Create one short reasoning task about {stage['practice_anchor']} for the learner. "
            "Keep it course-relevant and do not provide the full solution.",
            role="practice",
            system_prompt=practice_system_prompt(),
            required_terms=stage["required_terms"],
            forbidden_terms=["president", "executive branch", "code structure"],
            temperature=0.3,
            max_tokens=220,
            status_callback=emit_status,
        )
        turns.append(_format_turn("assistant", "Didactopus Practice Designer", practice_stage))

        evaluator_stage = _generate_checked(
            provider,
            f"Give short evaluator feedback on this learner reflection in the context of {stage['topic']}: "
            f"{learner_stage}\nTask context: {practice_stage}",
            role="evaluator",
            system_prompt=evaluator_system_prompt(),
            required_terms=["correctness", "explanation", *stage["required_terms"][:2]],
            forbidden_terms=["president", "executive branch", "code structure"],
            temperature=0.2,
            max_tokens=220,
            status_callback=emit_status,
        )
        turns.append(_format_turn("assistant", "Didactopus Evaluator", evaluator_stage))

    return {
        "provider": config.model_provider.provider,
        "skill": context.skill_name,
        "course": context.pack.get("display_name", context.pack.get("name", "")),
        "curriculum_path_titles": path_titles,
        "role_fallbacks": role_fallbacks,
        "status_updates": status_updates,
        "transcript": turns,
    }


def write_transcript_artifacts(payload: dict, out_dir: str | Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "rolemesh_transcript.json"
    md_path = out_dir / "rolemesh_transcript.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Local LLM Transcript: MIT OCW Information and Entropy",
        "",
        f"- Provider: `{payload['provider']}`",
        f"- Skill: `{payload['skill']}`",
        f"- Course: `{payload['course']}`",
        "",
    ]
    if payload.get("status_updates"):
        lines.append("## Pending Status Examples")
        for update in payload["status_updates"][:8]:
            lines.append(f"- {update}")
        lines.append("")
    for turn in payload["transcript"]:
        lines.append(f"## {turn['speaker']}")
        lines.append(turn["content"])
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def run_ocw_rolemesh_transcript_demo(config_path: str | Path, skill_dir: str | Path, out_dir: str | Path) -> dict:
    payload = build_ocw_rolemesh_transcript(config_path, skill_dir)
    outputs = write_transcript_artifacts(payload, out_dir)
    payload["artifacts"] = outputs
    return payload


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate a transcript of an AI learner using a local LLM path to approach the MIT OCW Information and Entropy course.")
    parser.add_argument("--config", default=str(root / "configs" / "config.rolemesh.example.yaml"))
    parser.add_argument("--skill-dir", default=str(root / "skills" / "ocw-information-entropy-agent"))
    parser.add_argument("--out-dir", default=str(root / "examples" / "ocw-information-entropy-rolemesh-transcript"))
    args = parser.parse_args()
    payload = run_ocw_rolemesh_transcript_demo(args.config, args.skill_dir, args.out_dir)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
