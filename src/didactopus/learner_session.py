from __future__ import annotations

from dataclasses import dataclass
import re

from .model_provider import ModelProvider
from .ocw_skill_agent_demo import (
    SkillContext,
    _match_concepts,
    build_skill_grounded_study_plan,
    evaluate_submission_with_skill,
)
from .provider_policy import effective_provider_for_kind
from .language_support import response_language_instruction
from .role_prompts import system_prompt_for_role


def _grounding_block(step: dict) -> str:
    fragments = step.get("source_fragments", []) or []
    fragment_lines = [fragment.get("text", "") for fragment in fragments if fragment.get("text")]
    lines = [
        f"Concept: {step.get('title', '')}",
        f"Prerequisites: {', '.join(step.get('prerequisite_titles', []) or ['none explicit'])}",
        f"Supporting lessons: {', '.join(step.get('supporting_lessons', []) or [step.get('title', '')])}",
    ]
    if step.get("session_goal"):
        lines.append(f"Session goal: {step.get('session_goal')}")
    if step.get("evidence_focus"):
        lines.append(f"Evidence focus: {step.get('evidence_focus')}")
    if step.get("next_transition"):
        lines.append(f"Next transition: {step.get('next_transition')}")
    scaffold_record = step.get("scaffold_record") or {}
    if scaffold_record.get("question"):
        lines.append(f"Scaffold question: {scaffold_record.get('question')}")
    if scaffold_record.get("verification_prompt"):
        lines.append(f"Verification prompt: {scaffold_record.get('verification_prompt')}")
    if scaffold_record.get("misconception_guard"):
        lines.append(f"Misconception guard: {scaffold_record.get('misconception_guard')}")
    if scaffold_record.get("didactopus_prompt_seed"):
        lines.append(f"Prompt seed: {scaffold_record.get('didactopus_prompt_seed')}")
    if fragment_lines:
        lines.append("Grounding fragments:")
        lines.extend(f"- {line}" for line in fragment_lines)
    return "\n".join(lines)


def _scaffold_instruction_block(step: dict) -> str:
    scaffold_record = step.get("scaffold_record") or {}
    lines: list[str] = []
    if scaffold_record.get("verification_prompt"):
        lines.append(f"Use this verification prompt directly: {scaffold_record.get('verification_prompt')}")
    if scaffold_record.get("didactopus_prompt_seed"):
        lines.append(f"Use this prompt-seed move directly: {scaffold_record.get('didactopus_prompt_seed')}")
    if scaffold_record.get("misconception_guard"):
        lines.append(
            f"Guard against this misconception explicitly: {scaffold_record.get('misconception_guard')}"
        )
    return "\n".join(lines)


def _generate_role_text(
    provider: ModelProvider,
    *,
    role: str,
    prompt: str,
    language: str = "en",
    source_language: str = "en",
    temperature: float = 0.2,
    max_tokens: int = 220,
) -> str:
    return provider.generate(
        f"{prompt}{response_language_instruction(language, source_language)}",
        role=role,
        system_prompt=system_prompt_for_role(role),
        temperature=temperature,
        max_tokens=max_tokens,
    ).text.strip()


@dataclass
class LearnerSessionTurn:
    role: str
    label: str
    content: str


def _evaluate_notebook_sequence_submission(step: dict, learner_submission: str) -> dict:
    submission = learner_submission.strip()
    word_count = len(submission.split())
    scaffold_record = step.get("scaffold_record") or {}
    evidence_terms = {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z\-]+", step.get("evidence_focus", ""))
        if len(token) > 3
    }
    submission_terms = {
        token.lower() for token in re.findall(r"[A-Za-z][A-Za-z\-]+", submission)
    }
    matched_terms = sorted(evidence_terms & submission_terms)
    verdict = "acceptable" if word_count >= 12 and matched_terms else "needs_revision"
    return {
        "verdict": verdict,
        "aggregated": {
            "word_count": word_count,
            "matched_evidence_terms": matched_terms,
            "evidence_focus": step.get("evidence_focus", ""),
            "verification_prompt": scaffold_record.get("verification_prompt", ""),
            "misconception_guard": scaffold_record.get("misconception_guard", ""),
        },
    }


def build_graph_grounded_session(
    context: SkillContext,
    provider: ModelProvider,
    learner_goal: str,
    learner_submission: str,
    language: str = "en",
    source_language: str = "en",
) -> dict:
    provider = effective_provider_for_kind(provider, kind="chat")
    study_plan = build_skill_grounded_study_plan(context, learner_goal)
    steps = study_plan.get("steps", [])
    if not steps:
        raise ValueError("No grounded study-plan steps available for learner session.")

    primary = steps[0]
    secondary = steps[1] if len(steps) > 1 else primary
    mentor_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Learner goal: {learner_goal}\n"
        "Respond as Didactopus mentor. Give a short grounded orientation, explain why these concepts come first, "
        "and ask one focused question that keeps the learner doing the reasoning."
    )
    mentor_text = _generate_role_text(
        provider,
        role="mentor",
        prompt=mentor_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=260,
    )

    practice_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"Learner goal: {learner_goal}\n"
        "Create one reasoning-heavy practice task for the learner. Keep it grounded in the supporting lessons and do not provide the full solution."
    )
    practice_text = _generate_role_text(
        provider,
        role="practice",
        prompt=practice_prompt,
        language=language,
        source_language=source_language,
        temperature=0.3,
        max_tokens=220,
    )

    evaluation = evaluate_submission_with_skill(context, primary["concept_key"].split("::", 1)[-1], learner_submission)
    evaluator_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"Practice task: {practice_text}\n"
        f"Learner submission: {learner_submission}\n"
        f"Deterministic evaluator result: verdict={evaluation['verdict']}, aggregated={evaluation['aggregated']}\n"
        "Respond as Didactopus evaluator. Summarize strengths, real gaps, and one next revision target without pretending supported caveats are missing."
    )
    evaluator_text = _generate_role_text(
        provider,
        role="evaluator",
        prompt=evaluator_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=240,
    )

    next_step_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Evaluator feedback: {evaluator_text}\n"
        "Respond as Didactopus mentor. Give the next study action and explain why it follows from the grounded concept path."
    )
    next_step_text = _generate_role_text(
        provider,
        role="mentor",
        prompt=next_step_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=220,
    )

    turns = [
        LearnerSessionTurn(role="user", label="Learner Goal", content=learner_goal),
        LearnerSessionTurn(role="assistant", label="Didactopus Mentor", content=mentor_text),
        LearnerSessionTurn(role="assistant", label="Didactopus Practice Designer", content=practice_text),
        LearnerSessionTurn(role="user", label="Learner Submission", content=learner_submission),
        LearnerSessionTurn(role="assistant", label="Didactopus Evaluator", content=evaluator_text),
        LearnerSessionTurn(role="assistant", label="Didactopus Mentor", content=next_step_text),
    ]

    return {
        "goal": learner_goal,
        "output_language": language,
        "source_language": source_language,
        "study_plan": study_plan,
        "primary_concept": primary,
        "secondary_concept": secondary,
        "practice_task": practice_text,
        "evaluation": evaluation,
        "turns": [turn.__dict__ for turn in turns],
    }


def build_notebook_sequence_grounded_session(
    session_plan: dict,
    provider: ModelProvider,
    *,
    step_index: int,
    learner_submission: str,
    learner_goal: str | None = None,
    language: str = "en",
    source_language: str = "en",
) -> dict:
    provider = effective_provider_for_kind(provider, kind="chat")
    sessions = session_plan.get("sessions", [])
    if not sessions:
        raise ValueError("No notebook sequence sessions available for learner session.")
    if step_index < 0 or step_index >= len(sessions):
        raise IndexError(f"Step index {step_index} out of range for {len(sessions)} sessions.")

    primary = sessions[step_index]
    secondary = sessions[step_index + 1] if step_index + 1 < len(sessions) else primary
    resolved_goal = learner_goal or session_plan.get("learner_goal") or primary.get("session_goal", "")

    mentor_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Learner goal: {resolved_goal}\n"
        "Respond as Didactopus mentor. Give a short grounded orientation for this step, explain why it belongs here in the sequence, "
        "and ask one focused question that makes the learner produce a public reasoning move."
    )
    mentor_text = _generate_role_text(
        provider,
        role="mentor",
        prompt=mentor_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=260,
    )

    practice_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_scaffold_instruction_block(primary)}\n\n"
        f"Learner goal: {resolved_goal}\n"
        "Create one reasoning-heavy practice task for the learner. Use the verification prompt and prompt seed if provided. "
        "Keep it grounded in this concept step and do not provide the full solution."
    )
    practice_text = _generate_role_text(
        provider,
        role="practice",
        prompt=practice_prompt,
        language=language,
        source_language=source_language,
        temperature=0.3,
        max_tokens=220,
    )

    evaluation = _evaluate_notebook_sequence_submission(primary, learner_submission)
    evaluator_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_scaffold_instruction_block(primary)}\n\n"
        f"Practice task: {practice_text}\n"
        f"Learner submission: {learner_submission}\n"
        f"Deterministic evaluator result: verdict={evaluation['verdict']}, aggregated={evaluation['aggregated']}\n"
        "Respond as Didactopus evaluator. Use the verification prompt and misconception guard if provided. "
        "Summarize strengths, real gaps, and one next revision target without pretending supported caveats are missing."
    )
    evaluator_text = _generate_role_text(
        provider,
        role="evaluator",
        prompt=evaluator_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=240,
    )

    next_step_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Evaluator feedback: {evaluator_text}\n"
        "Respond as Didactopus mentor. Give the next study action and explain why it follows from this reviewed Notebook sequence."
    )
    next_step_text = _generate_role_text(
        provider,
        role="mentor",
        prompt=next_step_prompt,
        language=language,
        source_language=source_language,
        temperature=0.2,
        max_tokens=220,
    )

    turns = [
        LearnerSessionTurn(role="user", label="Learner Goal", content=resolved_goal),
        LearnerSessionTurn(role="assistant", label="Didactopus Mentor", content=mentor_text),
        LearnerSessionTurn(role="assistant", label="Didactopus Practice Designer", content=practice_text),
        LearnerSessionTurn(role="user", label="Learner Submission", content=learner_submission),
        LearnerSessionTurn(role="assistant", label="Didactopus Evaluator", content=evaluator_text),
        LearnerSessionTurn(role="assistant", label="Didactopus Mentor", content=next_step_text),
    ]

    return {
        "goal": resolved_goal,
        "output_language": language,
        "source_language": source_language,
        "study_plan": {
            "sequence_id": session_plan.get("sequence_id"),
            "sequence_title": session_plan.get("sequence_title"),
            "steps": sessions,
        },
        "primary_concept": primary,
        "secondary_concept": secondary,
        "practice_task": practice_text,
        "evaluation": evaluation,
        "turns": [turn.__dict__ for turn in turns],
    }
