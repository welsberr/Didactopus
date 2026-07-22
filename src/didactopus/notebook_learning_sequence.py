from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import urlsplit


EXPECTED_SCHEMA = "didactopus.notebook.learning_sequence.v1"
LEGACY_SCHEMAS = {"evo-edu.notebook.didactopus_learning_sequence.v1"}
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NOTEBOOK_ROOT = REPOSITORY_ROOT / "examples" / "notebook-learning-sequence"
DEFAULT_SEQUENCE_PATH = DEFAULT_NOTEBOOK_ROOT / "learning-paths" / "guided-core.didactopus.json"
DEFAULT_SELECTION_POLICY_PATH = DEFAULT_NOTEBOOK_ROOT / "learning-paths" / "guided-core.selection-policy.json"
EXPECTED_POLICY_SCHEMA = "didactopus.notebook_scaffold_selection_policy.v1"


def load_notebook_learning_sequence(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") not in {EXPECTED_SCHEMA, *LEGACY_SCHEMAS}:
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
    route_path = urlsplit(concept_url).path
    if not route_path.endswith(".html"):
        return None
    if route_path.startswith("/notebook/"):
        route_path = route_path.removeprefix("/notebook/")
    else:
        route_path = route_path.lstrip("/")
    relative = Path(route_path).with_suffix(".scaffold.json")
    root = Path(notebook_root).resolve()
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Scaffold path escapes notebook root: {concept_url!r}")
    return candidate


def scaffold_path_for_step(
    step: dict,
    *,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
) -> Path | None:
    explicit_path = step.get("scaffold_path")
    if explicit_path:
        root = Path(notebook_root).resolve()
        candidate = (root / explicit_path).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"Scaffold path escapes notebook root: {explicit_path!r}")
        return candidate
    return scaffold_path_for_concept_url(step.get("url", ""), notebook_root=notebook_root)


def load_notebook_concept_scaffold_for_step(
    step: dict,
    *,
    notebook_root: str | Path = DEFAULT_NOTEBOOK_ROOT,
) -> dict | None:
    scaffold_path = scaffold_path_for_step(step, notebook_root=notebook_root)
    if scaffold_path is None or not scaffold_path.exists():
        return None
    return json.loads(scaffold_path.read_text(encoding="utf-8"))


def select_scaffold_record_for_step(
    step: dict,
    scaffold: dict | None,
    *,
    selection_policy: dict | None = None,
) -> dict | None:
    if not scaffold:
        return None
    records = scaffold.get("records") or []
    if not records:
        return None
    policy = selection_policy or {
        "concept_type_preferences": {},
        "trigger_type_preferences": [],
    }
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
    selection_policy_path: str | Path | None = DEFAULT_SELECTION_POLICY_PATH,
) -> dict:
    payload = load_notebook_learning_sequence(path)
    selection_policy = (
        load_notebook_scaffold_selection_policy(selection_policy_path)
        if selection_policy_path is not None
        else None
    )
    sessions: list[dict] = []
    for step in payload["sequence"]:
        scaffold = load_notebook_concept_scaffold_for_step(step, notebook_root=notebook_root)
        selected_record = select_scaffold_record_for_step(
            step,
            scaffold,
            selection_policy=selection_policy,
        )
        scaffold_path = scaffold_path_for_step(step, notebook_root=notebook_root)
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
                "scaffold_path": str(scaffold_path) if scaffold_path else None,
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
