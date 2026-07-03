from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from typing import Any

from .ai_learner_benchmark import (
    OllamaClient,
    _auc,
    _brier,
    _extract_json_object,
    g_estimate,
    normalize_skill_artifact,
    parse_answer,
    probability_true,
    strip_model_reasoning,
    summarize_rows,
)


EXPERIMENT_ID = "source-spine-transfer-v1"
SOURCE_ID = "tidepool-protocol-v1"
SOURCE_TITLE = "The Tidepool Protocol"
SOURCE_TEXT = """The county adopted the Tidepool Protocol after eelgrass seedlings failed in three coves: Alder, Birch, and Cormorant. The protocol required volunteers to mark living shoots after thirty days, record turbidity before planting, separate predator-exclusion cages from open plots, and publish failed plots as well as successful ones.

At Alder Cove, volunteers planted sixty shaded trays inside predator-exclusion cages and sixty shaded trays in open plots. After thirty days, forty-two caged trays still had living shoots, while eighteen open trays did. The report said this supported testing cages further at Alder, but it did not prove a countywide recovery method.

At Birch Cove, the planting team forgot the required turbidity readings. The report kept Birch in the public appendix but excluded it from cross-cove comparison. The appendix showed several healthy trays and several failed trays.

At Cormorant Cove, turbidity was recorded and matched Alder's range, but half the trays were planted two weeks late after a storm broke the dock. The report analyzed Cormorant separately because late planting could change survival independent of cages.

One councilor claimed that blue plankton glow on the first night proved that moonlight fertilizer caused the recovery. The report rejected that claim. It noted that nitrate runoff fell after an upstream dairy valve was repaired before planting began, and it warned that a single glowing night was not a causal test.

The report's conclusion was narrow: predator-exclusion cages may have helped at Alder, but the county should not generalize from one cove without comparable measurements. The report also said that publishing failed plots prevented survivorship bias and made later review possible."""

SOURCE_SPINE = [
    "The protocol covers eelgrass seedling restoration in Alder, Birch, and Cormorant coves.",
    "Required records: thirty-day living-shoot marks, turbidity before planting, caged/open plot separation, and failed-plot publication.",
    "Alder had comparable shaded trays: 42 of 60 caged trays retained living shoots versus 18 of 60 open trays.",
    "Birch lacked turbidity readings, so it stayed in the appendix but was excluded from cross-cove comparison.",
    "Cormorant matched Alder turbidity but had a late-planting confound after a storm broke the dock.",
    "The report rejected the moonlight-fertilizer claim and pointed to repaired dairy-valve runoff as a possible background change.",
    "The valid conclusion was narrow: cages may have helped at Alder, but countywide recovery was not established.",
    "Publishing failed plots was meant to prevent survivorship bias.",
]

SUMMARY_ONLY_BRIEF = """Source spine:
- The protocol concerns eelgrass restoration in Alder, Birch, and Cormorant coves.
- It requires thirty-day living-shoot counts, turbidity readings before planting, separated cage/open plots, and publication of failed plots.
- Alder showed better survival in caged trays than open trays: 42/60 versus 18/60.
- Birch lacked turbidity readings and was excluded from cross-cove comparison.
- Cormorant had a late-planting confound after a storm.
- The report rejected a moonlight-fertilizer causal claim.
- The report supports a narrow Alder cage hypothesis, not countywide generalization.
- Failed-plot publication guards against survivorship bias."""

FULL_DIDACTOPUS_BRIEF = """Didactopus mentorship script:

Orientation:
- Treat the source as an argument about evidence quality, not just a list of restoration facts.
- Separate direct source facts from causal conclusions and from unsupported public claims.

Source spine:
1. Protocol duties: thirty-day shoot marks, turbidity readings, caged/open separation, and failed-plot publication.
2. Alder comparison: 42/60 caged trays versus 18/60 open trays.
3. Birch limitation: no turbidity readings, so appendix only for cross-cove comparison.
4. Cormorant limitation: turbidity matched Alder, but late planting after a storm confounds comparison.
5. Rejected claim: blue plankton glow did not test moonlight fertilizer causation.
6. Plausible background change: nitrate runoff fell after an upstream dairy valve repair.
7. Proper conclusion: cages may have helped at Alder, but countywide recovery is not established.
8. Review guardrail: publishing failures reduces survivorship bias.

Worked examples:
- Claim: The report proved cages work countywide. Answer: false. Evidence: the conclusion was narrow and warned against countywide generalization.
- Claim: Birch should be used in the cross-cove comparison. Answer: false. Evidence: required turbidity readings were missing.
- Claim: Cormorant is a clean comparison because turbidity matched Alder. Answer: false. Evidence: late planting after the storm was a separate confound.

Retrieval practice:
- What two Alder counts must be kept together?
- Which cove lacked turbidity readings?
- Which cove had late planting after a storm?
- What causal claim did the report reject?
- What bias does failed-plot publication reduce?

Mentor guardrails:
- Do not turn "may have helped at Alder" into "proved countywide recovery."
- Do not treat a single glowing night as a causal experiment.
- Mark unsupported explanations as unknown rather than supplying a plausible ecological story."""

CAUSAL_TIMING_CALIBRATION_BRIEF = """Didactopus causal-timing and calibration script:

Orientation:
- Treat this as a source-grounding and causal-reasoning exercise.
- Keep four different things separate: protocol result, unsupported causal claim, background timing fact, and permissible conclusion.
- Give high confidence only when a source anchor decides the claim. Use low confidence or unknown when the notes do not decide it.

Source spine:
1. Protocol duties: thirty-day shoot marks, turbidity readings, caged/open separation, and failed-plot publication.
2. Cleanest treatment contrast: Alder had 42/60 caged trays versus 18/60 open trays with living shoots.
3. Birch limitation: missing turbidity readings block cross-cove comparison.
4. Cormorant limitation: late planting after a storm is a timing confound even though turbidity matched Alder.
5. Rejected causal claim: one night of blue plankton glow did not prove moonlight fertilizer caused recovery.
6. Background timing fact: nitrate runoff fell after an upstream dairy valve was repaired before planting began.
7. Narrow conclusion: cages may have helped at Alder, but the county should not generalize to all coves.
8. Review guardrail: failed plots must remain visible to avoid survivorship bias.

Causal-timing mini-spine:
- Claim source: a councilor proposed the moonlight-fertilizer explanation.
- Evidence problem: a single glowing night is not a causal test.
- Timing fact: the dairy valve repair happened before planting began.
- Conclusion boundary: neither the glowing night nor the valve repair turns Alder into countywide proof.

Worked contrast cases:
- True: The valve repair happened before planting began. The source says this directly.
- False: The report accepted moonlight fertilizer as the cause. The source says it rejected that claim.
- Unknown: The source does not identify which cove saw the blue plankton glow.

Confidence calibration:
- Use 0.95 only for direct source details retained in notes.
- Use 0.7 or 0.8 for source-grounded conclusions that require one reasoning step.
- Use 0.5 and answer unknown when the source or notes do not decide a claim.
- A correct answer at 0.5 is not mastery evidence for calibrated understanding."""

CONDITIONS = {
    "source_dump": {
        "label": "Source Dump",
        "brief": "Read the source and produce your own study notes. No mentor summary is provided.",
    },
    "summary_only": {
        "label": "Summary Only",
        "brief": SUMMARY_ONLY_BRIEF,
    },
    "full_didactopus": {
        "label": "Full Didactopus",
        "brief": FULL_DIDACTOPUS_BRIEF,
    },
    "causal_timing_calibration": {
        "label": "Causal Timing + Calibration",
        "brief": CAUSAL_TIMING_CALIBRATION_BRIEF,
    },
}


@dataclass(frozen=True)
class AssessmentItem:
    item_id: str
    phase: str
    env: str
    claim: str
    y: int
    source_anchor: str
    construct: str


PRE_ITEMS = [
    AssessmentItem("pre_c_01", "pre", "C", "The Tidepool Protocol concerned eelgrass seedlings in three coves.", 1, "eelgrass seedlings failed in three coves", "direct detail"),
    AssessmentItem("pre_c_02", "pre", "C", "Alder Cove had forty-two living shoots in caged trays after thirty days.", 1, "forty-two caged trays still had living shoots", "direct detail"),
    AssessmentItem("pre_c_03", "pre", "C", "Birch Cove had complete turbidity readings for cross-cove comparison.", 0, "forgot the required turbidity readings", "direct contradiction"),
    AssessmentItem("pre_k_01", "pre", "K", "The report's conclusion was countywide rather than cove-specific.", 0, "did not prove a countywide recovery method", "transfer conclusion"),
    AssessmentItem("pre_k_02", "pre", "K", "Publishing failed plots is relevant to avoiding survivorship bias.", 1, "publishing failed plots prevented survivorship bias", "bias recognition"),
    AssessmentItem("pre_k_03", "pre", "K", "A single glowing night was treated as enough to prove fertilizer causation.", 0, "single glowing night was not a causal test", "causal reasoning"),
]

POST_ITEMS = [
    AssessmentItem("post_c_01", "post", "C", "The protocol required turbidity to be recorded before planting.", 1, "record turbidity before planting", "direct detail"),
    AssessmentItem("post_c_02", "post", "C", "Alder compared shaded caged trays with shaded open trays.", 1, "sixty shaded trays inside predator-exclusion cages and sixty shaded trays in open plots", "direct comparison"),
    AssessmentItem("post_c_03", "post", "C", "Birch was excluded from cross-cove comparison because turbidity readings were missing.", 1, "excluded it from cross-cove comparison", "direct limitation"),
    AssessmentItem("post_c_04", "post", "C", "Cormorant was analyzed separately because half the trays were planted two weeks late.", 1, "half the trays were planted two weeks late", "direct limitation"),
    AssessmentItem("post_c_05", "post", "C", "The report accepted the councilor's moonlight-fertilizer explanation.", 0, "The report rejected that claim", "direct contradiction"),
    AssessmentItem("post_c_06", "post", "C", "The upstream dairy valve repair happened before planting began.", 1, "repaired before planting began", "direct sequence"),
    AssessmentItem("post_k_01", "post", "K", "The source supports further testing of cages at Alder more strongly than immediate countywide adoption.", 1, "supported testing cages further at Alder", "transfer conclusion"),
    AssessmentItem("post_k_02", "post", "K", "Using only the healthy Birch trays would be cherry-picking because the appendix also had failed trays.", 1, "several healthy trays and several failed trays", "bias transfer"),
    AssessmentItem("post_k_03", "post", "K", "Cormorant is not a clean replication of Alder because timing differed even though turbidity matched.", 1, "late planting could change survival independent of cages", "confound transfer"),
    AssessmentItem("post_k_04", "post", "K", "The blue plankton glow is an adequate causal test if it happened before recovery.", 0, "a single glowing night was not a causal test", "causal fallacy"),
    AssessmentItem("post_k_05", "post", "K", "The Alder result alone proves predator-exclusion cages caused countywide eelgrass recovery.", 0, "did not prove a countywide recovery method", "overgeneralization"),
    AssessmentItem("post_k_06", "post", "K", "Publishing failed plots improves later review by making unsuccessful evidence visible.", 1, "made later review possible", "method transfer"),
]

RETENTION_ITEMS = [
    AssessmentItem("ret_c_01", "retention", "C", "The protocol required failed plots to be published.", 1, "publish failed plots", "direct detail"),
    AssessmentItem("ret_c_02", "retention", "C", "Alder's open plots had eighteen trays with living shoots after thirty days.", 1, "eighteen open trays did", "direct detail"),
    AssessmentItem("ret_c_03", "retention", "C", "Birch was the cove with a late-planting storm confound.", 0, "At Cormorant Cove", "detail distinction"),
    AssessmentItem("ret_k_01", "retention", "K", "A careful mentor should warn against hasty generalization from Alder to every cove.", 1, "county should not generalize from one cove", "fallacy transfer"),
    AssessmentItem("ret_k_02", "retention", "K", "The report makes the moonlight-fertilizer explanation stronger than the runoff-change explanation.", 0, "rejected that claim", "causal transfer"),
    AssessmentItem("ret_k_03", "retention", "K", "Missing turbidity data affects whether Birch can be compared fairly with the other coves.", 1, "excluded it from cross-cove comparison", "method transfer"),
]

ARTIFACT_REQUIRED_TERMS = {
    "protocol": ("protocol", "eelgrass"),
    "alder_counts": ("42", "18", "alder"),
    "birch_turbidity": ("birch", "turbidity"),
    "cormorant_timing": ("cormorant", "late", "storm"),
    "moonlight_rejected": ("moonlight", "rejected"),
    "survivorship": ("survivorship", "failed plots"),
}

ARTIFACT_STRUCTURE_TERMS = {
    "source_spine": ("source spine",),
    "summary": ("source summary", "summary"),
    "retrieval": ("retrieval questions", "retrieval"),
    "answer_key": ("answer key",),
    "guardrail": ("guardrail", "unknown", "unsupported"),
}

ARTIFACT_FORBIDDEN_TERMS = (
    "proved countywide",
    "moonlight fertilizer caused",
    "birch had complete turbidity",
    "cormorant was clean",
)


def intervention_prompt(condition: str) -> str:
    config = CONDITIONS[condition]
    return (
        f"Source title: {SOURCE_TITLE}\n\n{SOURCE_TEXT}\n\n"
        f"Condition: {config['label']}\n\n{config['brief']}\n\n"
        "Return a JSON object only with keys study_notes, guardrails, and confidence_advice. "
        "study_notes must contain eight concise notes useful for a closed-book test. "
        "guardrails must contain three notes about unsupported or overgeneralized claims. "
        "confidence_advice must tell a learner when to answer unknown."
    )


def notes_text(mentorship_response: str) -> str:
    payload = _extract_json_object(mentorship_response)
    if not payload:
        return strip_model_reasoning(mentorship_response).strip()
    lines: list[str] = []
    for key in ("study_notes", "guardrails"):
        value = payload.get(key)
        if isinstance(value, list):
            lines.append(key.replace("_", " ").title() + ":")
            lines.extend(f"- {item}" for item in value)
        elif value:
            lines.append(key.replace("_", " ").title() + f": {value}")
    if payload.get("confidence_advice"):
        lines.append("Confidence Advice: " + str(payload["confidence_advice"]))
    return "\n".join(lines).strip()


def answer_prompt(item: AssessmentItem, *, evidence_context: str | None) -> str:
    if evidence_context:
        context = (
            "Use only these learner notes from the earlier source study. "
            "Do not use outside knowledge. If the notes do not decide the claim, answer unknown.\n\n"
            f"{evidence_context}"
        )
    else:
        context = "You have not been given this source. Prefer unknown when the claim depends on unavailable source details."
    return (
        f"{context}\n\n"
        "Classify the claim. Return one JSON object with keys answer, confidence, justification. "
        "answer must be exactly true, false, or unknown. confidence is your probability that your answer is correct; use 0.5 for unknown.\n"
        f"Claim: {item.claim}"
    )


def score_row(
    *,
    run_id: str,
    model: str,
    condition: str,
    item: AssessmentItem,
    parsed: dict[str, Any],
    raw: str,
    duration_seconds: float,
) -> dict[str, Any]:
    answer = parsed["answer"]
    confidence = parsed["confidence"]
    p_true = probability_true(answer, confidence)
    correct = (answer == "true" and item.y == 1) or (answer == "false" and item.y == 0)
    unknown = answer == "unknown"
    return {
        "run_id": run_id,
        "model_id": model,
        "condition": condition,
        "phase": item.phase,
        "item_id": item.item_id,
        "claim_id": item.item_id,
        "env": f"{condition}_{item.phase}_{item.env}",
        "clean_or_target": item.env,
        "construct": item.construct,
        "y": item.y,
        "p": round(p_true, 6),
        "answer": answer,
        "confidence": round(confidence, 6),
        "correct": int(correct),
        "unknown": int(unknown),
        "overconfident_wrong": int((not correct) and (not unknown) and confidence >= 0.7),
        "unsupported_source_blind": int(item.phase == "pre" and not unknown),
        "duration_seconds": round(duration_seconds, 3),
        "claim": item.claim,
        "justification": parsed.get("justification", ""),
        "response_span": raw.strip(),
        "source_anchor": item.source_anchor,
    }


def score_study_artifact(text: str) -> dict[str, Any]:
    lowered = text.lower()
    fact_hits = {
        key: all(term in lowered for term in terms)
        for key, terms in ARTIFACT_REQUIRED_TERMS.items()
    }
    structure_hits = {
        key: any(term in lowered for term in terms)
        for key, terms in ARTIFACT_STRUCTURE_TERMS.items()
    }
    hallucinations = [term for term in ARTIFACT_FORBIDDEN_TERMS if term in lowered]
    fact_score = sum(fact_hits.values()) / len(fact_hits)
    structure_score = sum(structure_hits.values()) / len(structure_hits)
    hallucination_penalty = min(0.4, 0.1 * len(hallucinations))
    score = max(0.0, 0.6 * fact_score + 0.4 * structure_score - hallucination_penalty)
    return {
        "score": round(score, 6),
        "fact_score": round(fact_score, 6),
        "structure_score": round(structure_score, 6),
        "hallucination_penalty": round(hallucination_penalty, 6),
        "fact_hits": fact_hits,
        "structure_hits": structure_hits,
        "hallucinations": hallucinations,
    }


def _condition_phase_rows(rows: list[dict[str, Any]], phase: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["phase"] == phase]


def summarize_condition_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for phase in ("pre", "post", "retention"):
        phase_rows = _condition_phase_rows(rows, phase)
        metrics[phase] = summarize_rows(phase_rows, phase)
        metrics[f"G_{phase}"] = g_estimate(phase_rows, phase)
    post_g = metrics["G_post"]["G"]
    pre_g = metrics["G_pre"]["G"]
    retention_g = metrics["G_retention"]["G"]
    metrics["delta_G_post"] = post_g - pre_g
    metrics["delta_G_retention"] = retention_g - pre_g
    metrics["normalized_delta_G_post"] = (post_g - pre_g) / max(1.0 - pre_g, 1e-12)
    metrics["normalized_delta_G_retention"] = (retention_g - pre_g) / max(1.0 - pre_g, 1e-12)
    return metrics


def run_condition(client: OllamaClient, model: str, condition: str, run_id: str) -> dict[str, Any]:
    system = {
        "role": "system",
        "content": (
            "You are an AI learner in a Didactopus source-spine transfer experiment. "
            "Answer from the provided learning evidence, preserve uncertainty, and do not invent source details."
        ),
    }
    rows: list[dict[str, Any]] = []
    interactions: list[dict[str, Any]] = []

    for item in PRE_ITEMS:
        started = time.time()
        raw = client.chat(
            model=model,
            messages=[system, {"role": "user", "content": answer_prompt(item, evidence_context=None)}],
            temperature=0.0,
            max_tokens=220,
            json_mode=True,
        )
        parsed = parse_answer(raw)
        rows.append(
            score_row(
                run_id=run_id,
                model=model,
                condition=condition,
                item=item,
                parsed=parsed,
                raw=raw,
                duration_seconds=time.time() - started,
            )
        )
        interactions.append({"phase": "pre", "item_id": item.item_id, "raw": raw, "parsed": parsed})

    mentor_messages = [system, {"role": "user", "content": intervention_prompt(condition)}]
    started = time.time()
    mentorship_response = client.chat(
        model=model,
        messages=mentor_messages,
        temperature=0.2,
        max_tokens=650,
        json_mode=True,
    )
    note_context = notes_text(mentorship_response)
    interactions.append(
        {
            "phase": "mentorship",
            "condition": condition,
            "raw": mentorship_response,
            "note_context": note_context,
            "duration_seconds": round(time.time() - started, 3),
        }
    )

    for item in POST_ITEMS:
        started = time.time()
        raw = client.chat(
            model=model,
            messages=[system, {"role": "user", "content": answer_prompt(item, evidence_context=note_context)}],
            temperature=0.0,
            max_tokens=240,
            json_mode=True,
        )
        parsed = parse_answer(raw)
        rows.append(
            score_row(
                run_id=run_id,
                model=model,
                condition=condition,
                item=item,
                parsed=parsed,
                raw=raw,
                duration_seconds=time.time() - started,
            )
        )
        interactions.append({"phase": "post", "item_id": item.item_id, "raw": raw, "parsed": parsed})

    for item in RETENTION_ITEMS:
        started = time.time()
        raw = client.chat(
            model=model,
            messages=[system, {"role": "user", "content": answer_prompt(item, evidence_context=note_context)}],
            temperature=0.0,
            max_tokens=240,
            json_mode=True,
        )
        parsed = parse_answer(raw)
        rows.append(
            score_row(
                run_id=run_id,
                model=model,
                condition=condition,
                item=item,
                parsed=parsed,
                raw=raw,
                duration_seconds=time.time() - started,
            )
        )
        interactions.append({"phase": "retention", "item_id": item.item_id, "raw": raw, "parsed": parsed})

    skill_prompt = (
        f"Source title: {SOURCE_TITLE}\n\nLearner notes:\n{note_context}\n\n"
        "Create a compact Didactopus study skill artifact from these notes. Return a JSON object only with keys: "
        "title, source_spine, source_summary, retrieval_questions, guardrail. source_spine must be an array of concise strings. "
        "retrieval_questions must be an array of three objects with question and answer keys."
    )
    started = time.time()
    skill_artifact = normalize_skill_artifact(
        client.chat(
            model=model,
            messages=[system, {"role": "user", "content": skill_prompt}],
            temperature=0.2,
            max_tokens=700,
            json_mode=True,
        )
    )
    skill_score = score_study_artifact(skill_artifact)
    interactions.append(
        {
            "phase": "derived_skill",
            "condition": condition,
            "raw": skill_artifact,
            "score": skill_score,
            "duration_seconds": round(time.time() - started, 3),
        }
    )

    return {
        "condition": condition,
        "condition_label": CONDITIONS[condition]["label"],
        "rows": rows,
        "interactions": interactions,
        "mentorship_response": mentorship_response,
        "note_context": note_context,
        "skill_artifact": skill_artifact,
        "skill_score": skill_score,
        "metrics": summarize_condition_rows(rows),
    }


def aggregate_condition_effects(models: list[dict[str, Any]]) -> dict[str, Any]:
    effects: dict[str, Any] = {}
    for condition in CONDITIONS:
        condition_runs = [condition_run for model in models for condition_run in model["conditions"] if condition_run["condition"] == condition]
        if not condition_runs:
            continue
        effects[condition] = {
            "n_models": len(condition_runs),
            "mean_post_accuracy": sum(run["metrics"]["post"].get("accuracy", 0.0) for run in condition_runs) / len(condition_runs),
            "mean_retention_accuracy": sum(run["metrics"]["retention"].get("accuracy", 0.0) for run in condition_runs) / len(condition_runs),
            "mean_delta_G_post": sum(run["metrics"]["delta_G_post"] for run in condition_runs) / len(condition_runs),
            "mean_delta_G_retention": sum(run["metrics"]["delta_G_retention"] for run in condition_runs) / len(condition_runs),
            "mean_skill_score": sum(run["skill_score"]["score"] for run in condition_runs) / len(condition_runs),
        }
    return effects


def write_human_packets(out_dir: Path, run_id: str) -> dict[str, str]:
    participant_path = out_dir / "human_pilot_packet.md"
    mentor_path = out_dir / "human_mentor_condition_scripts.md"
    response_path = out_dir / "human_response_sheet.csv"
    answer_key_path = out_dir / "human_answer_key.csv"

    participant_path.write_text(render_human_participant_packet(), encoding="utf-8")
    mentor_path.write_text(render_human_mentor_scripts(run_id), encoding="utf-8")

    all_items = [*PRE_ITEMS, *POST_ITEMS, *RETENTION_ITEMS]
    with response_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["participant_id", "condition", "phase", "item_id", "claim", "answer", "confidence_0_to_1", "notes"])
        writer.writeheader()
        for item in all_items:
            writer.writerow(
                {
                    "participant_id": "",
                    "condition": "",
                    "phase": item.phase,
                    "item_id": item.item_id,
                    "claim": item.claim,
                    "answer": "",
                    "confidence_0_to_1": "",
                    "notes": "",
                }
            )

    with answer_key_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["phase", "item_id", "env", "construct", "y", "answer", "source_anchor", "claim"])
        writer.writeheader()
        for item in all_items:
            writer.writerow(
                {
                    "phase": item.phase,
                    "item_id": item.item_id,
                    "env": item.env,
                    "construct": item.construct,
                    "y": item.y,
                    "answer": "true" if item.y == 1 else "false",
                    "source_anchor": item.source_anchor,
                    "claim": item.claim,
                }
            )

    return {
        "human_pilot_packet": str(participant_path),
        "human_mentor_condition_scripts": str(mentor_path),
        "human_response_sheet": str(response_path),
        "human_answer_key": str(answer_key_path),
    }


def render_human_participant_packet() -> str:
    lines = [
        "# Human Pilot Packet: Source-Spine Transfer v1",
        "",
        "Purpose: test whether source-spine mentoring improves grounded, transferable, calibrated understanding.",
        "",
        "Participant instructions:",
        "- Answer each claim as true, false, or unknown.",
        "- Give confidence from 0.0 to 1.0. Use 0.5 for unknown.",
        "- Do not guess when the source or your notes do not decide the claim.",
        "- The delayed retention section should be completed later without the source.",
        "",
        "Confidence scale:",
        "- 0.5: unknown or not enough evidence",
        "- 0.6: weakly leaning",
        "- 0.8: likely",
        "- 0.95: very confident from source memory or notes",
        "",
        "Source:",
        "",
        SOURCE_TEXT,
        "",
        "Pretest, immediate posttest, transfer, and delayed-retention claims are in `human_response_sheet.csv`.",
    ]
    return "\n".join(lines) + "\n"


def render_human_mentor_scripts(run_id: str) -> str:
    lines = [
        "# Human Mentor Condition Scripts",
        "",
        f"Run id: `{run_id}`",
        "",
        "Assign participants to one condition. Keep timing, source exposure, and response collection consistent.",
        "",
    ]
    for condition, config in CONDITIONS.items():
        lines.extend(
            [
                f"## {config['label']} (`{condition}`)",
                "",
                "Give the participant the source and this condition script. Ask them to make brief study notes before testing.",
                "",
                config["brief"],
                "",
            ]
        )
    lines.extend(
        [
            "## Delayed Retention",
            "",
            "Collect the retention section 24-72 hours later, without the source. Participants may use their own notes only if the pilot condition allows notes.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict[str, Any], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows = [row for model in payload["models"] for condition in model["conditions"] for row in condition["rows"]]
    scored_path = out_dir / "scored_claims.csv"
    row_fields = [
        "run_id",
        "model_id",
        "condition",
        "phase",
        "item_id",
        "claim_id",
        "env",
        "clean_or_target",
        "construct",
        "y",
        "p",
        "answer",
        "confidence",
        "correct",
        "unknown",
        "overconfident_wrong",
        "unsupported_source_blind",
        "duration_seconds",
        "claim",
        "justification",
        "response_span",
        "source_anchor",
    ]
    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=row_fields)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({field: row.get(field, "") for field in row_fields})

    for model in payload["models"]:
        model_name = safe_name(model["model_id"])
        for condition in model["conditions"]:
            condition_name = condition["condition"]
            (out_dir / f"notes_{model_name}_{condition_name}.md").write_text(condition["note_context"] + "\n", encoding="utf-8")
            (out_dir / f"derived_skill_{model_name}_{condition_name}.md").write_text(condition["skill_artifact"], encoding="utf-8")
            interactions_path = out_dir / f"interactions_{model_name}_{condition_name}.jsonl"
            with interactions_path.open("w", encoding="utf-8") as handle:
                for interaction in condition["interactions"]:
                    handle.write(json.dumps(interaction) + "\n")

    human_paths = write_human_packets(out_dir, payload["run_id"])
    report_path = out_dir / "groundedness_report.md"
    report_path.write_text(render_report(payload), encoding="utf-8")
    manifest_path = out_dir / "source_spine_transfer_run.json"
    payload["artifacts"] = {
        "manifest": str(manifest_path),
        "scored_claims": str(scored_path),
        "report": str(report_path),
        **human_paths,
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload["artifacts"]


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Source-Spine Transfer Experiment Report",
        "",
        f"- Run id: `{payload['run_id']}`",
        f"- Experiment: `{EXPERIMENT_ID}`",
        f"- Source: `{SOURCE_TITLE}` (`{SOURCE_ID}`)",
        f"- Ollama base URL: `{payload['ollama_base_url']}`",
        "- AI posttest mode: source-hidden, learner-notes-only assessment.",
        "- Human packet: same source and answer key, suitable for closed-book or notes-only delayed retention.",
        "",
        "## Condition Summary",
        "",
        "| Condition | Mean post acc | Mean retention acc | Mean Delta G post | Mean Delta G retention | Mean skill |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, effect in payload["condition_effects"].items():
        lines.append(
            f"| `{condition}` | {effect['mean_post_accuracy']:.3f} | {effect['mean_retention_accuracy']:.3f} | "
            f"{effect['mean_delta_G_post']:.3f} | {effect['mean_delta_G_retention']:.3f} | {effect['mean_skill_score']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Model And Condition Detail",
            "",
            "| Model | Condition | Pre unk | Post acc | Retention acc | G pre | G post | G retention | Skill |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model in payload["models"]:
        for condition in model["conditions"]:
            metrics = condition["metrics"]
            lines.append(
                f"| `{model['model_id']}` | `{condition['condition']}` | "
                f"{metrics['pre'].get('unknown_rate', 0):.3f} | {metrics['post'].get('accuracy', 0):.3f} | "
                f"{metrics['retention'].get('accuracy', 0):.3f} | {metrics['G_pre']['G']:.3f} | "
                f"{metrics['G_post']['G']:.3f} | {metrics['G_retention']['G']:.3f} | "
                f"{condition['skill_score']['score']:.3f} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- Source-blind pretest abstention is expected; unsupported confident pretest answers are counted separately.",
            "- Posttest and retention are notes-only for the AI learners. This tests whether each condition produces usable study notes, not whether the model can reread the source.",
            "- `G` is a point estimate over direct/source-near `C` rows and shifted/transfer `K` rows.",
            "- The human packet should be treated as a pilot instrument; human results need consent, anonymization, and separate analysis.",
        ]
    )
    return "\n".join(lines) + "\n"


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def run_experiment(
    *,
    models: list[str],
    conditions: list[str],
    out_dir: str | Path,
    ollama_base_url: str,
    timeout: float,
) -> dict[str, Any]:
    unknown_conditions = [condition for condition in conditions if condition not in CONDITIONS]
    if unknown_conditions:
        raise ValueError(f"Unknown conditions: {', '.join(unknown_conditions)}")

    run_id = "source-spine-transfer-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = OllamaClient(ollama_base_url, timeout=timeout)
    payload: dict[str, Any] = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "source": {
            "source_id": SOURCE_ID,
            "title": SOURCE_TITLE,
            "text": SOURCE_TEXT,
            "source_spine": SOURCE_SPINE,
        },
        "conditions_requested": conditions,
        "ollama_base_url": ollama_base_url,
        "models": [],
    }
    for model in models:
        model_payload = {"model_id": model, "conditions": []}
        for condition in conditions:
            model_payload["conditions"].append(run_condition(client, model, condition, run_id))
        payload["models"].append(model_payload)
    payload["condition_effects"] = aggregate_condition_effects(payload["models"])
    payload["artifacts"] = write_outputs(payload, Path(out_dir))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the source-spine transfer mentorship experiment.")
    parser.add_argument("--models", nargs="+", default=["gemma4:e4b", "qwen3:30b"])
    parser.add_argument("--conditions", nargs="+", default=list(CONDITIONS))
    parser.add_argument("--out-dir", default="examples/ai-learner-mentorship/source-spine-transfer-latest")
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=240.0)
    args = parser.parse_args()
    payload = run_experiment(
        models=args.models,
        conditions=args.conditions,
        out_dir=args.out_dir,
        ollama_base_url=args.ollama_base_url,
        timeout=args.timeout,
    )
    print(json.dumps({"run_id": payload["run_id"], "artifacts": payload["artifacts"]}, indent=2))


if __name__ == "__main__":
    main()
