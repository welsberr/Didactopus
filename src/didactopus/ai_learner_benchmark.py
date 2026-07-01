from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import time
from typing import Any
from urllib import request


SOURCE_ID = "glass-orchard-v1"
SOURCE_TITLE = "The Glass Orchard"
SOURCE_TEXT = """Mara Venn kept the Glass Orchard in the lantern room of a disused lighthouse. The orchard had twelve pear trees blown from green glass, and each tree opened its blossoms only while the foghorn was silent.

Her apprentice Ivo believed the trees disliked copper. On the third night he replaced Mara's copper watering can with a blue enamel kettle. The cracked third tree sealed itself before dawn, leaving a thin silver scar.

A clockwork moth named Pilgrim carried pollen between the branches, but only when wound counterclockwise. If Pilgrim was wound the other way, it landed on the lighthouse map and tapped the reef named Saint Orra.

During the autumn storm, the western panes shattered and salt rain entered the lantern room. Mara had time to save either the root ledger or the silver pruning shears. She saved the ledger, and the shears rusted shut.

At sunrise, Mara and Ivo planted one real apple seed inside a cracked bell jar. It made the first living leaf the orchard had ever grown, and the bell jar hummed in C-sharp."""

MENTORSHIP_BRIEF = """Study-aid layers for the source:

At-a-glance orientation:
- This is a compact fictional source about a glass orchard maintained by Mara Venn and her apprentice Ivo in a disused lighthouse.
- The key learning task is to keep concrete source details separate from plausible inventions.

Source spine:
1. Setting: lantern room of a disused lighthouse.
2. Orchard rule: twelve green-glass pear trees bloom only while the foghorn is silent.
3. Ivo's intervention: copper can replaced by a blue enamel kettle; the cracked third tree heals with a silver scar.
4. Pilgrim's rule: the clockwork moth pollinates only when wound counterclockwise; otherwise it taps Saint Orra on the map.
5. Storm choice: Mara saves the root ledger instead of the silver pruning shears.
6. Final change: a real apple seed in a cracked bell jar grows the orchard's first living leaf; the jar hums in C-sharp.

Worked example:
Claim: Mara saved the silver pruning shears during the storm.
Answer: false.
Evidence: The source says she had to choose between the root ledger and the shears, saved the ledger, and the shears rusted shut.

Retrieval practice:
- What material were the pear trees made from?
- What did Ivo replace?
- What winding direction made Pilgrim carry pollen?
- What did Mara save during the storm?
- What was living rather than glass at the end?

Mentor guardrail:
If a detail is not in the source, mark it unknown or unsupported instead of inventing a plausible answer."""


@dataclass(frozen=True)
class ClaimItem:
    item_id: str
    env: str
    claim: str
    y: int
    source_anchor: str


PRETEST_ITEMS = [
    ClaimItem("pre_c_01", "C", "Mara Venn kept the Glass Orchard in the lantern room of a disused lighthouse.", 1, "lantern room of a disused lighthouse"),
    ClaimItem("pre_c_02", "C", "The orchard contained twelve green-glass pear trees.", 1, "twelve pear trees blown from green glass"),
    ClaimItem("pre_c_03", "C", "Ivo replaced a copper watering can with a red clay pitcher.", 0, "blue enamel kettle"),
    ClaimItem("pre_c_04", "C", "Pilgrim was a clockwork moth.", 1, "A clockwork moth named Pilgrim"),
    ClaimItem("pre_c_05", "C", "Mara saved the silver pruning shears during the storm.", 0, "She saved the ledger"),
    ClaimItem("pre_c_06", "C", "The first living leaf came from a real apple seed.", 1, "one real apple seed"),
    ClaimItem("pre_k_01", "K", "The healed third tree retained visible evidence of its old crack.", 1, "thin silver scar"),
    ClaimItem("pre_k_02", "K", "Copper is shown as helpful to the glass trees.", 0, "Ivo believed the trees disliked copper"),
    ClaimItem("pre_k_03", "K", "Pilgrim's wrong winding direction was associated with Saint Orra rather than pollination.", 1, "tapped the reef named Saint Orra"),
    ClaimItem("pre_k_04", "K", "Mara's storm choice suggests she valued the root ledger over the pruning shears.", 1, "She saved the ledger"),
    ClaimItem("pre_k_05", "K", "The final new life in the orchard was a pear blossom from a glass tree.", 0, "real apple seed"),
    ClaimItem("pre_k_06", "K", "The bell jar made a sound after the living leaf appeared.", 1, "hummed in C-sharp"),
]

POSTTEST_ITEMS = [
    ClaimItem("post_c_01", "C", "The Glass Orchard was kept in a working clock tower.", 0, "disused lighthouse"),
    ClaimItem("post_c_02", "C", "The glass trees bloomed only while the foghorn was silent.", 1, "only while the foghorn was silent"),
    ClaimItem("post_c_03", "C", "The cracked third tree healed after Ivo used a blue enamel kettle.", 1, "blue enamel kettle"),
    ClaimItem("post_c_04", "C", "Pilgrim carried pollen when wound clockwise.", 0, "only when wound counterclockwise"),
    ClaimItem("post_c_05", "C", "The silver pruning shears rusted shut after the storm.", 1, "the shears rusted shut"),
    ClaimItem("post_c_06", "C", "The bell jar hummed in B-flat.", 0, "hummed in C-sharp"),
    ClaimItem("post_k_01", "K", "A reader should treat Saint Orra as connected to Pilgrim's failed winding, not to successful pollination.", 1, "landed on the lighthouse map and tapped the reef named Saint Orra"),
    ClaimItem("post_k_02", "K", "The story contrasts artificial glass growth with one final living plant.", 1, "first living leaf the orchard had ever grown"),
    ClaimItem("post_k_03", "K", "The storm destroyed the root ledger.", 0, "She saved the ledger"),
    ClaimItem("post_k_04", "K", "The source supports the claim that Ivo proved all metal was harmful to the orchard.", 0, "disliked copper"),
    ClaimItem("post_k_05", "K", "The third tree's silver scar is evidence that healing did not erase every sign of damage.", 1, "thin silver scar"),
    ClaimItem("post_k_06", "K", "The final living plant was grown outside the lighthouse after Mara abandoned the orchard.", 0, "inside a cracked bell jar"),
]

SKILL_REQUIRED_FACTS = {
    "mara": ("mara",),
    "ivo": ("ivo",),
    "pilgrim": ("pilgrim", "clockwork moth"),
    "ledger_choice": ("root ledger", "ledger"),
    "apple_seed": ("apple seed", "living leaf"),
    "c_sharp": ("c-sharp", "c sharp"),
}

SKILL_STRUCTURE_TERMS = {
    "source_spine": ("source spine", "sequence", "setting"),
    "summary": ("summary", "overview", "at-a-glance"),
    "retrieval": ("retrieval", "quiz", "question"),
    "answer_key": ("answer key", "answers"),
    "guardrail": ("unknown", "unsupported", "do not invent", "not in the source"),
}

SKILL_FORBIDDEN_TERMS = (
    "clock tower",
    "red clay pitcher",
    "clockwise for pollination",
    "nightingale",
    "peach",
    "b-flat",
    "working lighthouse",
)


class OllamaClient:
    def __init__(self, base_url: str, timeout: float = 180.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 320,
        json_mode: bool = False,
    ) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"
        req = request.Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        message = body.get("message", {})
        content = message.get("content", "")
        text = content if isinstance(content, str) else str(content)
        return strip_model_reasoning(text)


def strip_model_reasoning(text: str) -> str:
    """Remove visible thinking blocks some local thinking models emit."""
    cleaned = re.sub(r"(?is)<think>.*?</think>\s*", "", text)
    think_close = re.search(r"(?i)</think>\s*", cleaned)
    if think_close:
        cleaned = cleaned[think_close.end() :]
    return cleaned.lstrip()


def clean_skill_artifact(text: str) -> str:
    cleaned = strip_model_reasoning(text)
    section_start = re.search(r"(?im)^(?:\*\*)?(?:artifact\s+)?title\s*:", cleaned)
    if not section_start:
        section_start = re.search(r"(?im)^(?:\*\*)?source spine\s*:", cleaned)
    if section_start and section_start.start() > 0:
        cleaned = cleaned[section_start.start() :]
    return cleaned.strip() + ("\n" if cleaned.strip() else "")


def normalize_skill_artifact(text: str) -> str:
    cleaned = clean_skill_artifact(text)
    payload = _extract_json_object(cleaned)
    if not payload:
        return cleaned

    title = str(payload.get("title") or SOURCE_TITLE).strip()
    source_spine = _string_list(payload.get("source_spine"))
    source_summary = str(payload.get("source_summary") or payload.get("summary") or "").strip()
    guardrail = str(payload.get("guardrail") or "").strip()
    retrieval_questions = _retrieval_pairs(payload.get("retrieval_questions"))

    lines = [f"Title: {title}", "", "Source Spine:"]
    for item in source_spine:
        lines.append(f"- {item}")
    if not source_spine:
        lines.append("-")
    lines.extend(["", "Source Summary:", source_summary or ""])
    lines.extend(["", "Retrieval Questions:"])
    for index, pair in enumerate(retrieval_questions, start=1):
        lines.append(f"{index}. {pair['question']}")
    if not retrieval_questions:
        lines.append("1.")
    lines.extend(["", "Answer Key:"])
    for index, pair in enumerate(retrieval_questions, start=1):
        lines.append(f"{index}. {pair['answer']}")
    if not retrieval_questions:
        lines.append("1.")
    lines.extend(["", "Guardrail:", guardrail or ""])
    return "\n".join(lines).strip() + "\n"


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [line.strip(" -") for line in value.splitlines() if line.strip(" -")]
    return []


def _retrieval_pairs(value: Any) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    if not isinstance(value, list):
        return pairs
    for item in value:
        if isinstance(item, dict):
            question = str(item.get("question") or item.get("q") or "").strip()
            answer = str(item.get("answer") or item.get("a") or "").strip()
        else:
            question = str(item).strip()
            answer = ""
        if question or answer:
            pairs.append({"question": question, "answer": answer})
    return pairs


def _answer_prompt(item: ClaimItem, *, source_visible: bool) -> str:
    if source_visible:
        source_note = (
            f"Use this source and mentorship brief as your evidence.\n\nSource title: {SOURCE_TITLE}\n\n"
            f"{SOURCE_TEXT}\n\nMentorship brief:\n{MENTORSHIP_BRIEF}\n\n"
            "Answer true when the claim is supported, false when it is contradicted, "
            "and unknown only when the source genuinely does not decide the claim."
        )
    else:
        source_note = (
            "You have not been given this source. Prefer unknown when the claim depends on unavailable source details."
        )
    return (
        f"{source_note}\n"
        "Classify the claim. Return a single JSON object with keys answer, confidence, justification.\n"
        "answer must be exactly true, false, or unknown. confidence is your probability that your answer is correct; use 0.5 for unknown.\n"
        f"Claim: {item.claim}"
    )


def parse_answer(text: str) -> dict[str, Any]:
    payload = _extract_json_object(text)
    if payload:
        answer = str(payload.get("answer", "unknown")).strip().lower()
        if answer not in {"true", "false", "unknown"}:
            answer = _fallback_answer(text)
        confidence = _coerce_confidence(payload.get("confidence", 0.5))
        justification = str(payload.get("justification", "")).strip()
    else:
        answer = _fallback_answer(text)
        confidence = _fallback_confidence(text, answer)
        justification = text.strip()
    if answer == "unknown":
        confidence = 0.5
    return {"answer": answer, "confidence": confidence, "justification": justification}


def _extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    candidates = [stripped]
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if match:
        candidates.insert(0, match.group(0))
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _fallback_answer(text: str) -> str:
    lowered = text.lower()
    if re.search(r"\bunknown\b|\bnot enough information\b|\bnot provided\b|\bcannot determine\b", lowered):
        return "unknown"
    if re.search(r"\bfalse\b|\bincorrect\b|\bnot true\b", lowered):
        return "false"
    if re.search(r"\btrue\b|\bcorrect\b", lowered):
        return "true"
    return "unknown"


def _coerce_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.5
    if confidence > 1.0 and confidence <= 100.0:
        confidence /= 100.0
    return min(max(confidence, 0.0), 1.0)


def _fallback_confidence(text: str, answer: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match:
        return _coerce_confidence(float(match.group(1)))
    match = re.search(r"\b(?:confidence|probability)\D+(\d+(?:\.\d+)?)", text.lower())
    if match:
        return _coerce_confidence(float(match.group(1)))
    return 0.5 if answer == "unknown" else 0.7


def probability_true(answer: str, confidence: float) -> float:
    if answer == "true":
        return confidence
    if answer == "false":
        return 1.0 - confidence
    return 0.5


def score_row(model: str, phase: str, item: ClaimItem, parsed: dict[str, Any], raw: str) -> dict[str, Any]:
    answer = parsed["answer"]
    confidence = parsed["confidence"]
    p_true = probability_true(answer, confidence)
    correct = (answer == "true" and item.y == 1) or (answer == "false" and item.y == 0)
    unknown = answer == "unknown"
    return {
        "run_id": "",
        "model_id": model,
        "phase": phase,
        "item_id": item.item_id,
        "claim_id": item.item_id,
        "env": f"{phase}_{item.env}",
        "clean_or_target": item.env,
        "y": item.y,
        "p": round(p_true, 6),
        "answer": answer,
        "confidence": round(confidence, 6),
        "correct": int(correct),
        "unknown": int(unknown),
        "overconfident_wrong": int((not correct) and (not unknown) and confidence >= 0.7),
        "unsupported_source_blind": int(phase == "pre" and not unknown),
        "claim": item.claim,
        "justification": parsed.get("justification", ""),
        "response_span": raw.strip(),
        "source_anchor": item.source_anchor,
    }


def _brier(rows: list[dict[str, Any]]) -> float:
    return sum((float(row["p"]) - int(row["y"])) ** 2 for row in rows) / len(rows) if rows else 0.0


def _auc(rows: list[dict[str, Any]]) -> float:
    positives = [float(row["p"]) for row in rows if int(row["y"]) == 1]
    negatives = [float(row["p"]) for row in rows if int(row["y"]) == 0]
    if not positives or not negatives:
        return 0.5
    wins = 0.0
    total = len(positives) * len(negatives)
    for pos in positives:
        for neg in negatives:
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / total


def _norm_brier(brier: float, prevalence: float) -> float:
    baseline = max(prevalence * (1.0 - prevalence), 1e-12)
    return min(max(1.0 - brier / baseline, 0.0), 1.0)


def _norm_auc(auc: float) -> float:
    return min(max((auc - 0.5) / 0.5, 0.0), 1.0)


def _robust_auc(auc_clean: float, auc_target: float) -> float:
    denom = max(auc_clean - 0.5, 1e-12)
    return min(max(1.0 - (auc_clean - auc_target) / denom, 0.0), 1.0)


def g_estimate(rows: list[dict[str, Any]], phase: str) -> dict[str, Any]:
    clean = [row for row in rows if row["phase"] == phase and row["clean_or_target"] == "C"]
    target = [row for row in rows if row["phase"] == phase and row["clean_or_target"] == "K"]
    if not clean or not target:
        return {"G": 0.0, "components": {}, "n": {"clean": len(clean), "target": len(target)}}
    prevalence = sum(int(row["y"]) for row in target) / len(target)
    brier_target = _brier(target)
    auc_target = _auc(target)
    auc_clean = _auc(clean)
    s_t = _norm_brier(brier_target, prevalence)
    s_d = _norm_auc(auc_target)
    s_r = _robust_auc(auc_clean, auc_target)
    return {
        "G": (s_t + s_d + s_r) / 3.0,
        "components": {
            "S_T": {"point": s_t, "brier": brier_target, "prevalence": prevalence},
            "S_D": {"point": s_d, "auc_target": auc_target},
            "S_R": {"point": s_r, "auc_clean": auc_clean, "auc_target": auc_target},
        },
        "n": {"clean": len(clean), "target": len(target)},
    }


def summarize_rows(rows: list[dict[str, Any]], phase: str) -> dict[str, Any]:
    selected = [row for row in rows if row["phase"] == phase]
    if not selected:
        return {}
    return {
        "n": len(selected),
        "accuracy": sum(int(row["correct"]) for row in selected) / len(selected),
        "unknown_rate": sum(int(row["unknown"]) for row in selected) / len(selected),
        "overconfident_wrong_rate": sum(int(row["overconfident_wrong"]) for row in selected) / len(selected),
        "unsupported_source_blind_rate": sum(int(row["unsupported_source_blind"]) for row in selected) / len(selected),
        "brier": _brier(selected),
        "auc": _auc(selected),
    }


def score_skill_artifact(text: str) -> dict[str, Any]:
    lowered = text.lower()
    fact_hits = {
        key: any(term in lowered for term in terms)
        for key, terms in SKILL_REQUIRED_FACTS.items()
    }
    structure_hits = {
        key: any(term in lowered for term in terms)
        for key, terms in SKILL_STRUCTURE_TERMS.items()
    }
    hallucinations = [term for term in SKILL_FORBIDDEN_TERMS if term in lowered]
    fact_score = sum(fact_hits.values()) / len(fact_hits)
    structure_score = sum(structure_hits.values()) / len(structure_hits)
    hallucination_penalty = min(0.3, 0.1 * len(hallucinations))
    total = max(0.0, 0.6 * fact_score + 0.4 * structure_score - hallucination_penalty)
    return {
        "score": round(total, 6),
        "fact_score": round(fact_score, 6),
        "structure_score": round(structure_score, 6),
        "hallucination_penalty": round(hallucination_penalty, 6),
        "fact_hits": fact_hits,
        "structure_hits": structure_hits,
        "hallucinations": hallucinations,
    }


def run_model(client: OllamaClient, model: str, run_id: str) -> dict[str, Any]:
    system = {
        "role": "system",
        "content": (
            "You are an AI learner in a Didactopus mentorship benchmark. "
            "Answer from evidence, preserve uncertainty, and do not invent source details."
        ),
    }
    pre_messages = [system]
    pre_rows = []
    interactions: list[dict[str, Any]] = []
    for item in PRETEST_ITEMS:
        messages = [*pre_messages, {"role": "user", "content": _answer_prompt(item, source_visible=False)}]
        started = time.time()
        raw = client.chat(model=model, messages=messages, temperature=0.0, max_tokens=220, json_mode=True)
        parsed = parse_answer(raw)
        row = score_row(model, "pre", item, parsed, raw)
        row["run_id"] = run_id
        row["duration_seconds"] = round(time.time() - started, 3)
        pre_rows.append(row)
        interactions.append({"phase": "pre", "item_id": item.item_id, "raw": raw, "parsed": parsed})

    mentor_messages = [
        system,
        {
            "role": "user",
            "content": (
                f"Source title: {SOURCE_TITLE}\n\n{SOURCE_TEXT}\n\n{MENTORSHIP_BRIEF}\n\n"
                "Before testing, return a JSON object with keys study_notes and guardrails. "
                "study_notes must contain five concise source-grounded notes. guardrails must contain two uncertainties or guardrails. "
                "Return only the JSON object, with no analysis or preamble."
            ),
        },
    ]
    started = time.time()
    mentorship_response = client.chat(model=model, messages=mentor_messages, temperature=0.2, max_tokens=420, json_mode=True)
    mentor_messages.append({"role": "assistant", "content": mentorship_response})
    interactions.append(
        {
            "phase": "mentorship",
            "raw": mentorship_response,
            "duration_seconds": round(time.time() - started, 3),
        }
    )

    post_rows = []
    for item in POSTTEST_ITEMS:
        messages = [*mentor_messages, {"role": "user", "content": _answer_prompt(item, source_visible=True)}]
        started = time.time()
        raw = client.chat(model=model, messages=messages, temperature=0.0, max_tokens=220, json_mode=True)
        parsed = parse_answer(raw)
        row = score_row(model, "post", item, parsed, raw)
        row["run_id"] = run_id
        row["duration_seconds"] = round(time.time() - started, 3)
        post_rows.append(row)
        interactions.append({"phase": "post", "item_id": item.item_id, "raw": raw, "parsed": parsed})

    skill_prompt = (
        "Create a compact Didactopus study skill artifact for this source. Return a JSON object only with keys: "
        "title, source_spine, source_summary, retrieval_questions, guardrail. source_spine must be an array of concise strings. "
        "retrieval_questions must be an array of three objects with question and answer keys. Do not include analysis or preamble."
    )
    started = time.time()
    skill_artifact = normalize_skill_artifact(client.chat(
        model=model,
        messages=[*mentor_messages, {"role": "user", "content": skill_prompt}],
        temperature=0.2,
        max_tokens=700,
        json_mode=True,
    ))
    skill_score = score_skill_artifact(skill_artifact)
    interactions.append(
        {
            "phase": "derived_skill",
            "raw": skill_artifact,
            "score": skill_score,
            "duration_seconds": round(time.time() - started, 3),
        }
    )

    rows = [*pre_rows, *post_rows]
    g_pre = g_estimate(rows, "pre")
    g_post = g_estimate(rows, "post")
    delta_g = g_post["G"] - g_pre["G"]
    normalized_delta_g = delta_g / max(1.0 - g_pre["G"], 1e-12)
    return {
        "model_id": model,
        "rows": rows,
        "interactions": interactions,
        "mentorship_response": mentorship_response,
        "skill_artifact": skill_artifact,
        "skill_score": skill_score,
        "metrics": {
            "pre": summarize_rows(rows, "pre"),
            "post": summarize_rows(rows, "post"),
            "G_pre": g_pre,
            "G_post": g_post,
            "delta_G": delta_g,
            "normalized_delta_G": normalized_delta_g,
        },
    }


def write_outputs(payload: dict[str, Any], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows = [row for model in payload["models"] for row in model["rows"]]
    row_fields = [
        "run_id",
        "model_id",
        "phase",
        "item_id",
        "claim_id",
        "env",
        "clean_or_target",
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
    scored_path = out_dir / "scored_claims.csv"
    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=row_fields)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({field: row.get(field, "") for field in row_fields})

    manifest_path = out_dir / "ai_learner_bench_run.json"
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    for model in payload["models"]:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", model["model_id"])
        (out_dir / f"derived_skill_{safe_name}.md").write_text(model["skill_artifact"], encoding="utf-8")
        interactions_path = out_dir / f"interactions_{safe_name}.jsonl"
        with interactions_path.open("w", encoding="utf-8") as handle:
            for interaction in model["interactions"]:
                handle.write(json.dumps(interaction) + "\n")

    report_path = out_dir / "groundedness_report.md"
    report_path.write_text(render_report(payload), encoding="utf-8")
    return {
        "manifest": str(manifest_path),
        "scored_claims": str(scored_path),
        "report": str(report_path),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# AI Learner Mentorship Benchmark Report",
        "",
        f"- Run id: `{payload['run_id']}`",
        f"- Source: `{SOURCE_TITLE}` (`{SOURCE_ID}`)",
        f"- Condition: `{payload['condition']}`",
        f"- Ollama base URL: `{payload['ollama_base_url']}`",
        "",
        "## Model Summary",
        "",
        "| Model | Pre accuracy | Post accuracy | Pre unknown | Post unknown | G pre | G post | Delta G | Skill score |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model in payload["models"]:
        metrics = model["metrics"]
        pre = metrics["pre"]
        post = metrics["post"]
        lines.append(
            f"| `{model['model_id']}` | {pre.get('accuracy', 0):.3f} | {post.get('accuracy', 0):.3f} | "
            f"{pre.get('unknown_rate', 0):.3f} | {post.get('unknown_rate', 0):.3f} | "
            f"{metrics['G_pre']['G']:.3f} | {metrics['G_post']['G']:.3f} | "
            f"{metrics['delta_G']:.3f} | {model['skill_score']['score']:.3f} |"
        )
    lines.extend(["", "## Interpretation Notes", ""])
    lines.append("- Pretest is source-blind; abstention is expected and unsupported confident answers are counted separately.")
    lines.append("- Posttest is source-visible and follows a source-grounded mentorship turn.")
    lines.append("- `G` is a point estimate using target-transfer rows as `K` and direct/source-near rows as `C`; this first run has no bootstrap CI.")
    lines.append("- Skill score is a deterministic first-pass rubric over required source facts, study-aid structure, and obvious hallucination terms.")
    return "\n".join(lines) + "\n"


def run_benchmark(
    *,
    models: list[str],
    out_dir: str | Path,
    ollama_base_url: str,
    timeout: float,
) -> dict[str, Any]:
    run_id = "ai-learner-glass-orchard-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = OllamaClient(ollama_base_url, timeout=timeout)
    payload = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "condition": "source_visible_posttest_with_scripted_mentorship",
        "source": {
            "source_id": SOURCE_ID,
            "title": SOURCE_TITLE,
            "text": SOURCE_TEXT,
            "mentorship_brief": MENTORSHIP_BRIEF,
        },
        "ollama_base_url": ollama_base_url,
        "models": [],
    }
    for model in models:
        payload["models"].append(run_model(client, model, run_id))
    payload["artifacts"] = write_outputs(payload, Path(out_dir))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a compact AI-learner mentorship benchmark.")
    parser.add_argument("--models", nargs="+", default=["gemma4:e4b", "qwen3:30b"])
    parser.add_argument("--out-dir", default="examples/ai-learner-mentorship/glass-orchard-latest")
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=240.0)
    args = parser.parse_args()
    payload = run_benchmark(
        models=args.models,
        out_dir=args.out_dir,
        ollama_base_url=args.ollama_base_url,
        timeout=args.timeout,
    )
    print(json.dumps({"run_id": payload["run_id"], "artifacts": payload["artifacts"]}, indent=2))


if __name__ == "__main__":
    main()
