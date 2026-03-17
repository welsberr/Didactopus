from __future__ import annotations

from dataclasses import dataclass

from .language_support import response_language_instruction
from .model_provider import ModelProvider
from .ocw_skill_agent_demo import (
    SkillContext,
    _match_concepts,
    build_skill_grounded_study_plan,
    evaluate_submission_with_skill,
)
from .role_prompts import system_prompt_for_role


def _grounding_block(step: dict) -> str:
    fragments = step.get("source_fragments", []) or []
    fragment_lines = [fragment.get("text", "") for fragment in fragments if fragment.get("text")]
    lines = [
        f"Concept: {step.get('title', '')}",
        f"Prerequisites: {', '.join(step.get('prerequisite_titles', []) or ['none explicit'])}",
        f"Supporting lessons: {', '.join(step.get('supporting_lessons', []) or [step.get('title', '')])}",
    ]
    if fragment_lines:
        lines.append("Grounding fragments:")
        lines.extend(f"- {line}" for line in fragment_lines)
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


def build_graph_grounded_session(
    context: SkillContext,
    provider: ModelProvider,
    learner_goal: str,
    learner_submission: str,
    language: str = "en",
    source_language: str = "en",
) -> dict:
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
