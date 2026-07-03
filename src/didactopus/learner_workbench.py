from __future__ import annotations

import json
from pathlib import Path

import yaml

from .config import AppConfig
from .graph_retrieval import graph_quality_summary, load_groundrecall_graph_interchange
from .model_provider import ModelProvider
from .role_prompts import system_prompt_for_role


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_PACKS = ROOT / "domain-packs"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_groundrecall_summary(pack_dir: Path) -> dict:
    interchange_summary = _load_groundrecall_interchange_summary(pack_dir)
    path = pack_dir / "groundrecall_query_bundle.json"
    if not path.exists():
        return interchange_summary
    payload = json.loads(path.read_text(encoding="utf-8"))
    review_candidates = payload.get("review_candidates", []) or []
    concept = payload.get("concept", {}) or {}
    graph_codes = sorted(
        {
            code
            for item in review_candidates
            for code in item.get("finding_codes", []) or []
            if "concept" in str(code) or "bridge" in str(code) or "component" in str(code)
        }
    )
    top_rationales = [str(item.get("rationale", "")).strip() for item in review_candidates if str(item.get("rationale", "")).strip()][:3]
    source_role_summary = payload.get("source_role_summary", {}) or {}
    key_distinctions = payload.get("key_distinctions", []) or []
    secondary_products = payload.get("review_context", {}).get("secondary_products", {}) if isinstance(payload.get("review_context"), dict) else {}
    summary = {
        "concept_id": concept.get("concept_id", ""),
        "concept_title": concept.get("title", ""),
        "review_candidate_count": len(review_candidates),
        "graph_codes": graph_codes,
        "top_rationales": top_rationales,
        "source_role_summary": source_role_summary,
        "key_distinctions": key_distinctions[:5],
        "secondary_products": secondary_products,
    }
    if interchange_summary:
        summary.update(
            {
                "graph_interchange_included": True,
                "graph_quality_summary": interchange_summary.get("graph_quality_summary", {}),
                "graph_node_count": interchange_summary.get("graph_node_count", 0),
                "graph_edge_count": interchange_summary.get("graph_edge_count", 0),
                "graph_consumer_notes": interchange_summary.get("graph_consumer_notes", []),
            }
        )
    return summary


def _load_groundrecall_interchange_summary(pack_dir: Path) -> dict:
    path = pack_dir / "graph_interchange.json"
    if not path.exists():
        return {}
    bundle = load_groundrecall_graph_interchange(path)
    return {
        "graph_interchange_included": True,
        "graph_node_count": len(bundle.knowledge_graph.get("nodes", []) or []),
        "graph_edge_count": len(bundle.knowledge_graph.get("edges", []) or []),
        "graph_quality_summary": graph_quality_summary(bundle),
        "graph_consumer_notes": bundle.knowledge_graph.get("consumer_notes", []) or [],
    }


def load_pack_context(pack_id: str) -> dict:
    pack_dir = DOMAIN_PACKS / pack_id
    if not pack_dir.exists():
        raise FileNotFoundError(f"Unknown pack: {pack_id}")
    pack = _load_yaml(pack_dir / "pack.yaml")
    concepts = (_load_yaml(pack_dir / "concepts.yaml")).get("concepts", []) or []
    by_id = {concept.get("id"): concept for concept in concepts}
    groundrecall = _load_groundrecall_summary(pack_dir)
    return {
      "pack_dir": pack_dir,
      "pack": pack,
      "concepts": concepts,
      "by_id": by_id,
      "groundrecall": groundrecall,
    }


def _scientific_virtues_block() -> str:
    return (
        "Scientific virtues operating guidance:\n"
        "- Distinguish observation from interpretation.\n"
        "- Preserve uncertainty where the evidence does not settle the issue.\n"
        "- Treat revision as progress when better evidence changes the conclusion.\n"
        "- Prefer source-grounded comparison over unsupported confidence."
    )


def _concept_block(concept: dict, by_id: dict[str, dict]) -> str:
    prerequisite_titles = [by_id.get(pid, {}).get("title", pid) for pid in concept.get("prerequisites", []) or []]
    mastery_signals = concept.get("mastery_signals", []) or []
    lines = [
        f"Concept: {concept.get('title', '')}",
        f"Prerequisites: {', '.join(prerequisite_titles or ['none explicit'])}",
        f"Description: {concept.get('description', '')}",
    ]
    if mastery_signals:
        lines.append("Mastery signals:")
        lines.extend(f"- {item}" for item in mastery_signals)
    return "\n".join(lines)


def _groundrecall_block(summary: dict) -> str:
    if not summary:
        return ""
    lines = [
        "GroundRecall context:",
        f"- Query concept: {summary.get('concept_title') or summary.get('concept_id') or 'unknown'}",
        f"- Review candidate count: {summary.get('review_candidate_count', 0)}",
    ]
    graph_codes = summary.get("graph_codes", []) or []
    if graph_codes:
        lines.append(f"- Structural signals: {', '.join(graph_codes)}")
    source_role_summary = summary.get("source_role_summary", {}) or {}
    if source_role_summary:
        lines.append(
            "- Source roles: "
            + ", ".join(f"{role}={count}" for role, count in sorted(source_role_summary.items()))
        )
    for item in summary.get("key_distinctions", []) or []:
        text = str(item.get("text", "")).strip()
        distinction_type = str(item.get("distinction_type", "")).strip()
        if text:
            lines.append(f"- Distinction ({distinction_type or 'contrast'}): {text}")
    secondary_products = summary.get("secondary_products", {}) or {}
    if secondary_products:
        lines.append(
            "- Secondary review products: "
            + ", ".join(f"{key}={value}" for key, value in sorted(secondary_products.items()) if value)
        )
    if summary.get("graph_interchange_included"):
        lines.append(
            f"- Graph interchange: nodes={summary.get('graph_node_count', 0)}, edges={summary.get('graph_edge_count', 0)}"
        )
    quality_summary = summary.get("graph_quality_summary", {}) or {}
    quality_parts = [
        f"{key}={value}"
        for key, value in sorted(quality_summary.items())
        if key in {"inferred_relation_count", "weakly_grounded_relation_count", "unsupported_claim_count", "high_fanout_concept_count"}
        and value
    ]
    if quality_parts:
        lines.append("- Graph quality signals: " + ", ".join(quality_parts))
    for rationale in summary.get("top_rationales", []) or []:
        lines.append(f"- Review cue: {rationale}")
    return "\n".join(lines)


def _generate(provider: ModelProvider, *, role: str, prompt: str, temperature: float, max_tokens: int) -> dict:
    response = provider.generate(
        prompt,
        role=role,
        system_prompt=system_prompt_for_role(role),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "text": response.text.strip(),
        "provider": response.provider,
        "model_name": response.model_name,
    }


def _feedback(question: str, observation: str, interpretation: str, uncertainty: str, revision_trigger: str) -> dict:
    strengths: list[str] = []
    gaps: list[str] = []
    if question.strip():
        strengths.append("You stated a concrete study question.")
    else:
        gaps.append("State a clear question before treating the inquiry as settled.")
    if observation.strip():
        strengths.append("You recorded an explicit observation.")
    else:
        gaps.append("Record what was observed before moving to interpretation.")
    if interpretation.strip():
        strengths.append("You proposed an interpretation.")
    else:
        gaps.append("State the interpretation you currently think fits best.")
    if uncertainty.strip():
        strengths.append("You preserved uncertainty instead of smoothing it away.")
    else:
        gaps.append("Name one uncertainty or limitation in the current explanation.")
    if revision_trigger.strip():
        strengths.append("You identified what evidence could justify revision.")
    else:
        gaps.append("Say what result or source would make you revise your view.")
    return {
        "strengths": strengths,
        "gaps": gaps,
        "next_revision_target": gaps[0] if gaps else "Compare one more source or example before treating the interpretation as stable.",
    }


def build_pack_workbench_session(
    *,
    pack_id: str,
    concept_id: str,
    learner_goal: str,
    question: str,
    observation: str,
    interpretation: str,
    uncertainty: str,
    revision_trigger: str,
) -> dict:
    context = load_pack_context(pack_id)
    pack = context["pack"]
    concepts = context["concepts"]
    by_id = context["by_id"]
    concept = by_id.get(concept_id) or (concepts[0] if concepts else None)
    if concept is None:
        raise KeyError(f"No concepts found for pack: {pack_id}")
    index = concepts.index(concept)
    next_concept = concepts[index + 1] if index + 1 < len(concepts) else concept

    provider = ModelProvider(AppConfig().model_provider)
    pack_block = (
        f"Pack: {pack.get('display_name', pack_id)}\n"
        f"Description: {pack.get('description', '')}\n"
        f"Audience level: {pack.get('audience_level', 'novice-friendly')}"
    )
    groundrecall_block = _groundrecall_block(context.get("groundrecall", {}))
    learner_state_block = (
        f"Learner goal: {learner_goal}\n"
        f"Question: {question}\n"
        f"Observation: {observation}\n"
        f"Interpretation: {interpretation}\n"
        f"Uncertainty: {uncertainty}\n"
        f"Revision trigger: {revision_trigger}"
    )

    mentor = _generate(
        provider,
        role="mentor",
        prompt=(
            f"{pack_block}\n\n{_concept_block(concept, by_id)}\n\n{_concept_block(next_concept, by_id)}\n\n"
            f"{_scientific_virtues_block()}\n\n"
            f"{groundrecall_block + chr(10) * 2 if groundrecall_block else ''}"
            f"{learner_state_block}\n"
            "Respond as Didactopus mentor. Give a short grounded orientation, explain why this concept matters now, "
            "and ask one focused question that helps the learner distinguish observation from interpretation."
        ),
        temperature=0.2,
        max_tokens=260,
    )
    practice = _generate(
        provider,
        role="practice",
        prompt=(
            f"{pack_block}\n\n{_concept_block(concept, by_id)}\n\n{_scientific_virtues_block()}\n\n"
            f"{groundrecall_block + chr(10) * 2 if groundrecall_block else ''}"
            f"{learner_state_block}\n"
            "Respond as Didactopus practice designer. Create one compact task that asks for evidence comparison, honest uncertainty, and a revision condition."
        ),
        temperature=0.25,
        max_tokens=220,
    )
    evaluator = _generate(
        provider,
        role="evaluator",
        prompt=(
            f"{pack_block}\n\n{_concept_block(concept, by_id)}\n\n{_scientific_virtues_block()}\n\n"
            f"{groundrecall_block + chr(10) * 2 if groundrecall_block else ''}"
            f"{learner_state_block}\n"
            "Respond as Didactopus evaluator. Name strengths first, then real gaps, and give one revision target without pretending stated caveats are absent."
        ),
        temperature=0.2,
        max_tokens=240,
    )
    next_step = _generate(
        provider,
        role="mentor",
        prompt=(
            f"{pack_block}\n\n{_concept_block(concept, by_id)}\n\n{_concept_block(next_concept, by_id)}\n\n"
            f"{_scientific_virtues_block()}\n\n"
            f"{groundrecall_block + chr(10) * 2 if groundrecall_block else ''}"
            f"Evaluator feedback: {evaluator['text']}\n"
            "Respond as Didactopus mentor. Give the next study action and say what new evidence or comparison would most help the learner revise or strengthen the current view."
        ),
        temperature=0.2,
        max_tokens=220,
    )

    feedback = _feedback(question, observation, interpretation, uncertainty, revision_trigger)
    return {
        "pack_id": pack_id,
        "concept_id": concept.get("id"),
        "concept_title": concept.get("title"),
        "next_concept_id": next_concept.get("id"),
        "next_concept_title": next_concept.get("title"),
        "groundrecall": context.get("groundrecall", {}),
        "mentor": mentor,
        "practice": practice,
        "evaluator": evaluator,
        "next_step": next_step,
        "feedback": feedback,
    }
