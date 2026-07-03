from __future__ import annotations

import json
from pathlib import Path
import re


EXPECTED_SCHEMA = "evo-edu.notebook.didactopus_learning_sequence.v1"
DEFAULT_NOTEBOOK_ROOT = Path(__file__).resolve().parents[2].parent / "evo-edu.org" / "notebook"
DEFAULT_SELECTION_POLICY_PATH = DEFAULT_NOTEBOOK_ROOT / "learning-paths" / "foundations-first-ring.selection-policy.json"
EXPECTED_POLICY_SCHEMA = "didactopus.notebook_scaffold_selection_policy.v1"


def load_notebook_learning_sequence(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise ValueError(
            f"Unsupported learning-sequence schema: {payload.get('schema')!r}"
        )
    sequence = payload.get("sequence")
    if not isinstance(sequence, list) or not sequence:
        raise ValueError("Learning-sequence payload must contain a non-empty sequence list.")
    return payload


def _tokenize(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z\-]+", text or "")
        if len(token) > 3
    }


def load_notebook_scaffold_selection_policy(
    path: str | Path = DEFAULT_SELECTION_POLICY_PATH,
) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_POLICY_SCHEMA:
        raise ValueError(
            f"Unsupported scaffold-selection policy schema: {payload.get('schema')!r}"
        )
    return payload


def scaffold_path_for_concept_url(
    concept_url: str,
    *,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
) -> Path | None:
    if not concept_url.startswith("/notebook/concepts/") or not concept_url.endswith(".html"):
        return None
    relative = concept_url.removeprefix("/notebook/").removesuffix(".html") + ".scaffold.json"
    return Path(notebook_root) / relative


def load_notebook_concept_scaffold_for_step(
    step: dict,
    *,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
) -> dict | None:
    concept_url = step.get("url", "")
    scaffold_path = scaffold_path_for_concept_url(concept_url, notebook_root=notebook_root)
    if scaffold_path is None or not scaffold_path.exists():
        return None
    return json.loads(scaffold_path.read_text(encoding="utf-8"))


def select_scaffold_record_for_step(step: dict, scaffold: dict | None) -> dict | None:
    if not scaffold:
        return None
    records = scaffold.get("records") or []
    if not records:
        return None
    policy = load_notebook_scaffold_selection_policy()
    step_terms = _tokenize(
        " ".join(
            [
                step.get("title", ""),
                step.get("session_goal", ""),
                step.get("mentor_opening", ""),
                step.get("evidence_focus", ""),
                step.get("next_transition", ""),
            ]
        )
    )
    preferred_types: list[str] = []
    preferred_types.extend(
        policy.get("concept_type_preferences", {}).get(step.get("concept_id", ""), [])
    )
    for rule in policy.get("trigger_type_preferences", []):
        trigger_terms = {term.lower() for term in rule.get("trigger_terms", [])}
        if step_terms & trigger_terms:
            preferred_types.extend(rule.get("preferred_types", []))
    type_rank: dict[str, int] = {}
    for index, record_type in enumerate(preferred_types):
        rank = len(preferred_types) - index
        current = type_rank.get(record_type, 0)
        if rank > current:
            type_rank[record_type] = rank
    scored: list[tuple[int, int, dict]] = []
    for index, record in enumerate(records):
        record_terms = _tokenize(
            " ".join(
                [
                    record.get("type", ""),
                    record.get("question", ""),
                    record.get("answer_summary", ""),
                    record.get("verification_prompt", ""),
                    record.get("misconception_guard", ""),
                    record.get("didactopus_prompt_seed", ""),
                ]
            )
        )
        lexical_score = len(step_terms & record_terms)
        preferred_score = type_rank.get(record.get("type", ""), 0)
        scored.append((preferred_score, lexical_score, -index, record))
    scored.sort(reverse=True)
    return scored[0][3]


def build_notebook_sequence_session_plan(
    path: str | Path,
    *,
    learner_goal: str | None = None,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
) -> dict:
    payload = load_notebook_learning_sequence(path)
    sessions: list[dict] = []
    for step in payload["sequence"]:
        scaffold = load_notebook_concept_scaffold_for_step(step, notebook_root=notebook_root)
        selected_record = select_scaffold_record_for_step(step, scaffold)
        sessions.append(
            {
                "position": step["position"],
                "concept_id": step["concept_id"],
                "title": step["title"],
                "url": step["url"],
                "session_goal": step["session_goal"],
                "mentor_opening": step["mentor_opening"],
                "evidence_focus": step["evidence_focus"],
                "next_transition": step["next_transition"],
                "scaffold_path": str(scaffold_path_for_concept_url(step["url"], notebook_root=notebook_root))
                if scaffold_path_for_concept_url(step["url"], notebook_root=notebook_root)
                else None,
                "scaffold_record_count": len((scaffold or {}).get("records", []) or []),
                "scaffold_pending_source_slots": len(
                    [
                        slot
                        for slot in (scaffold or {}).get("citegeist_source_slots", []) or []
                        if slot.get("review_status") == "pending"
                    ]
                ),
                "scaffold_record": selected_record,
            }
        )
    return {
        "sequence_id": payload["id"],
        "sequence_title": payload["title"],
        "sequence_kind": payload.get("sequence_kind"),
        "learner_goal": learner_goal
        or payload.get("learner_model", {}).get("intended_use")
        or "Use the reviewed Notebook concept order as a guided mentorship path.",
        "mentor_style": payload.get("learner_model", {}).get("mentor_style", []),
        "success_condition": payload.get("learner_model", {}).get("success_condition"),
        "session_count": len(sessions),
        "sessions": sessions,
    }
