from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Literal
from uuid import uuid4

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
    reliability_block = _reliability_context_block(step)
    if reliability_block:
        lines.append(reliability_block)
    citation_block = _citation_instruction_block(step)
    if citation_block:
        lines.append(citation_block)
    return "\n".join(lines)


def _format_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return "missing" if value is None or value == "" else str(value)


def _reliability_context_block(step: dict) -> str:
    context = step.get("reliability_context") or {}
    if not context:
        return ""
    heuristic = context.get("heuristic", {}) or {}
    bayesian = context.get("bayesian", {}) or {}
    interval = bayesian.get("credible_interval", {}) or {}
    lines = [
        "Graph reliability review context (not a truth label):",
        (
            f"- Heuristic band={_format_metric(heuristic.get('band'))}, "
            f"score={_format_metric(heuristic.get('score'))}"
        ),
        (
            f"- Bayesian classification={_format_metric(bayesian.get('classification'))}, "
            f"posterior mean={_format_metric(bayesian.get('posterior_mean'))}, "
            f"credible interval={_format_metric(interval.get('lower'))}..{_format_metric(interval.get('upper'))}, "
            f"width={_format_metric(bayesian.get('credible_interval_width'))}"
        ),
        (
            f"- Effective sample size={_format_metric(bayesian.get('effective_sample_size'))}, "
            f"prior-sensitivity range={_format_metric(bayesian.get('prior_sensitivity_range'))}"
        ),
        f"- Authority boundary: {context.get('authority', 'Review context only; not promotion authority.')}",
    ]
    return "\n".join(lines)


def _citation_anchors(step: dict) -> list[dict]:
    anchors: list[dict] = []
    seen: set[str] = set()
    for fragment in step.get("source_fragments", []) or []:
        fragment_id = str(fragment.get("fragment_id", "")).strip()
        source_refs = [str(item) for item in fragment.get("source_refs", []) or [] if str(item)]
        anchor_id = fragment_id or (source_refs[0] if source_refs else "")
        if not anchor_id or anchor_id in seen:
            continue
        seen.add(anchor_id)
        anchors.append(
            {
                "anchor_id": anchor_id,
                "fragment_id": fragment_id,
                "lesson_title": fragment.get("lesson_title", ""),
                "source_refs": source_refs,
            }
        )
    return anchors


def _citation_instruction_block(step: dict) -> str:
    anchors = _citation_anchors(step)
    if not anchors:
        return ""
    lines = [
        "Available source anchors (identification does not by itself establish claim support):"
    ]
    for anchor in anchors:
        refs = ", ".join(anchor["source_refs"]) or "no source reference supplied"
        lines.append(
            f"- {anchor['anchor_id']} | lesson={anchor['lesson_title']} | source={refs}"
        )
    return "\n".join(lines)


def build_citation_support_practice(step: dict, learner_submission: str) -> dict:
    anchors = _citation_anchors(step)
    submission_lower = learner_submission.lower()
    matched_anchor_ids: list[str] = []
    for anchor in anchors:
        candidates = [anchor["anchor_id"], anchor["fragment_id"], *anchor["source_refs"]]
        if any(candidate and candidate.lower() in submission_lower for candidate in candidates):
            matched_anchor_ids.append(anchor["anchor_id"])
    if not anchors:
        status = "not_available"
    elif matched_anchor_ids:
        status = "anchor_identified"
    else:
        status = "needs_source_anchor"
    return {
        "artifact_type": "citation_support_practice",
        "review_state": "draft",
        "status": status,
        "instruction": (
            "Identify the source anchor for one material claim, state what that source directly supports, "
            "and separate any additional inference."
        ),
        "available_anchors": anchors,
        "matched_anchor_ids": matched_anchor_ids,
        "mastery_effect": "none_until_review",
        "authority": (
            "Anchor matching confirms identification only; a reviewer must assess source identity, "
            "relevance, and whether the cited material supports the claim."
        ),
    }


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
    citation_support_practice = build_citation_support_practice(primary, learner_submission)
    mentor_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Learner goal: {learner_goal}\n"
        "Respond as Didactopus mentor. Give a short grounded orientation, explain why these concepts come first, "
        "and ask one focused question that keeps the learner doing the reasoning. Use reliability context to "
        "calibrate certainty, but never present it as a final truth label or learner mastery score."
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
        f"Citation-support instruction: {citation_support_practice['instruction']}\n"
        "Create one reasoning-heavy practice task for the learner. Keep it grounded in the supporting lessons, "
        "include the citation-support instruction when anchors are available, and do not provide the full solution."
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
        f"Citation-support check: status={citation_support_practice['status']}, "
        f"matched_anchor_ids={citation_support_practice['matched_anchor_ids']}\n"
        "Respond as Didactopus evaluator. Summarize strengths, real gaps, and one next revision target without pretending supported caveats are missing. "
        "Treat anchor matching as draft identification evidence, not proof that a source supports the claim. "
        "Use graph reliability only to calibrate feedback, never as a correctness verdict."
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
        "reliability_context": primary.get("reliability_context", {}),
        "citation_support_practice": citation_support_practice,
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
    citation_support_practice = build_citation_support_practice(primary, learner_submission)

    mentor_prompt = (
        f"{_grounding_block(primary)}\n\n"
        f"{_grounding_block(secondary)}\n\n"
        f"Learner goal: {resolved_goal}\n"
        "Respond as Didactopus mentor. Give a short grounded orientation for this step, explain why it belongs here in the sequence, "
        "and ask one focused question that makes the learner produce a public reasoning move. Use reliability context to "
        "calibrate certainty, but never present it as a final truth label or learner mastery score."
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
        f"Citation-support instruction: {citation_support_practice['instruction']}\n"
        "Create one reasoning-heavy practice task for the learner. Use the verification prompt and prompt seed if provided. "
        "When source anchors are available, require the learner to distinguish direct support from inference. "
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
        f"Citation-support check: status={citation_support_practice['status']}, "
        f"matched_anchor_ids={citation_support_practice['matched_anchor_ids']}\n"
        "Respond as Didactopus evaluator. Use the verification prompt and misconception guard if provided. "
        "Summarize strengths, real gaps, and one next revision target without pretending supported caveats are missing. "
        "Treat anchor matching as draft identification evidence, not proof that a source supports the claim. "
        "Use graph reliability only to calibrate feedback, never as a correctness verdict."
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
        "reliability_context": primary.get("reliability_context", {}),
        "citation_support_practice": citation_support_practice,
        "evaluation": evaluation,
        "turns": [turn.__dict__ for turn in turns],
    }


def build_notebook_sequence_grounded_run(
    session_plan: dict,
    provider: ModelProvider,
    *,
    learner_submissions: list[str],
    start_step_index: int = 0,
    learner_goal: str | None = None,
    language: str = "en",
    source_language: str = "en",
    learner_id: str = "local-learner",
    learner_kind: Literal["human", "ai_benchmark"] = "human",
    run_id: str | None = None,
    captured_at: str | None = None,
) -> dict:
    sessions = session_plan.get("sessions", [])
    if not sessions:
        raise ValueError("No notebook sequence sessions available for learner run.")
    if not learner_submissions:
        raise ValueError("A multi-step learner run requires at least one submission.")
    if learner_kind not in {"human", "ai_benchmark"}:
        raise ValueError("learner_kind must be 'human' or 'ai_benchmark'.")
    if start_step_index < 0 or start_step_index >= len(sessions):
        raise IndexError(
            f"Start step index {start_step_index} out of range for {len(sessions)} sessions."
        )
    end_step_index = start_step_index + len(learner_submissions)
    if end_step_index > len(sessions):
        available = len(sessions) - start_step_index
        raise ValueError(
            f"Received {len(learner_submissions)} submissions for {available} available steps."
        )

    resolved_run_id = run_id or str(uuid4())
    resolved_captured_at = captured_at or datetime.now(timezone.utc).isoformat()
    completed_sessions: list[dict] = []
    progress: list[dict] = []
    learner_evidence: list[dict] = []
    turns: list[dict] = []
    for offset, submission in enumerate(learner_submissions):
        step_index = start_step_index + offset
        session = build_notebook_sequence_grounded_session(
            session_plan=session_plan,
            provider=provider,
            step_index=step_index,
            learner_submission=submission,
            learner_goal=learner_goal,
            language=language,
            source_language=source_language,
        )
        completed_sessions.append(session)
        primary = session["primary_concept"]
        evaluation = session["evaluation"]
        progress.append(
            {
                "step_index": step_index,
                "position": primary.get("position"),
                "concept_id": primary.get("concept_id"),
                "title": primary.get("title"),
                "verdict": evaluation.get("verdict"),
                "matched_evidence_terms": evaluation.get("aggregated", {}).get(
                    "matched_evidence_terms",
                    [],
                ),
            }
        )
        learner_evidence.append(
            {
                "evidence_id": f"{resolved_run_id}:step:{step_index}",
                "artifact_type": "learner_attempt",
                "learner_id": learner_id,
                "learner_kind": learner_kind,
                "record_scope": "human_learner" if learner_kind == "human" else "benchmark",
                "review_state": "draft" if learner_kind == "human" else "benchmark_only",
                "captured_at": resolved_captured_at,
                "concept_id": primary.get("concept_id"),
                "concept_title": primary.get("title"),
                "dimension": "reasoning",
                "evidence_kind": "exercise",
                "source": {
                    "sequence_id": session_plan.get("sequence_id"),
                    "step_index": step_index,
                    "step_position": primary.get("position"),
                },
                "learner_submission": submission,
                "evaluator_assessment": evaluation,
                "citation_support_practice": session.get("citation_support_practice", {}),
                "mastery_effect": "none_until_review",
            }
        )
        for turn in session["turns"]:
            turns.append(
                {
                    **turn,
                    "step_index": step_index,
                    "step_position": primary.get("position"),
                    "concept_id": primary.get("concept_id"),
                    "concept_title": primary.get("title"),
                    "label": f"{primary.get('title', 'Sequence step')} — {turn['label']}",
                }
            )

    next_step_index = end_step_index if end_step_index < len(sessions) else None
    final_session = completed_sessions[-1]
    return {
        "schema_version": 1,
        "run_id": resolved_run_id,
        "learner_id": learner_id,
        "learner_kind": learner_kind,
        "created_at": resolved_captured_at,
        "updated_at": resolved_captured_at,
        "goal": final_session["goal"],
        "output_language": language,
        "source_language": source_language,
        "run_kind": "notebook_sequence",
        "status": "complete" if next_step_index is None else "in_progress",
        "study_plan": {
            "sequence_id": session_plan.get("sequence_id"),
            "sequence_title": session_plan.get("sequence_title"),
            "steps": sessions,
        },
        "start_step_index": start_step_index,
        "next_step_index": next_step_index,
        "completed_session_count": len(completed_sessions),
        "total_session_count": len(sessions),
        "progress": progress,
        "learner_evidence": learner_evidence,
        "sessions": completed_sessions,
        "evaluation": final_session["evaluation"],
        "turns": turns,
    }


def resume_notebook_sequence_grounded_run(
    session_plan: dict,
    provider: ModelProvider,
    *,
    previous_run: dict,
    learner_submissions: list[str],
    language: str | None = None,
    source_language: str | None = None,
    captured_at: str | None = None,
) -> dict:
    if previous_run.get("schema_version") != 1:
        raise ValueError("Unsupported learner run schema version.")
    if previous_run.get("run_kind") != "notebook_sequence":
        raise ValueError("Only notebook sequence runs can be resumed here.")
    sequence_id = session_plan.get("sequence_id")
    previous_sequence_id = previous_run.get("study_plan", {}).get("sequence_id")
    if sequence_id != previous_sequence_id:
        raise ValueError(
            f"Sequence mismatch: persisted run uses {previous_sequence_id!r}, not {sequence_id!r}."
        )
    next_step_index = previous_run.get("next_step_index")
    if next_step_index is None:
        raise ValueError("The persisted learner run is already complete.")
    if not learner_submissions:
        raise ValueError("Resuming a learner run requires at least one submission.")

    continuation = build_notebook_sequence_grounded_run(
        session_plan=session_plan,
        provider=provider,
        learner_submissions=learner_submissions,
        start_step_index=next_step_index,
        learner_goal=previous_run.get("goal"),
        language=language or previous_run.get("output_language", "en"),
        source_language=source_language or previous_run.get("source_language", "en"),
        learner_id=previous_run.get("learner_id", "local-learner"),
        learner_kind=previous_run.get("learner_kind", "human"),
        run_id=previous_run.get("run_id"),
        captured_at=captured_at,
    )
    combined = {
        **previous_run,
        **continuation,
        "created_at": previous_run.get("created_at", continuation["created_at"]),
        "start_step_index": previous_run.get("start_step_index", 0),
        "progress": [*previous_run.get("progress", []), *continuation["progress"]],
        "learner_evidence": [
            *previous_run.get("learner_evidence", []),
            *continuation["learner_evidence"],
        ],
        "sessions": [*previous_run.get("sessions", []), *continuation["sessions"]],
        "turns": [*previous_run.get("turns", []), *continuation["turns"]],
    }
    combined["completed_session_count"] = len(combined["sessions"])
    return combined
