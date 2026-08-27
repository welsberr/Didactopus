"""Versioned, deterministic learning-path pedagogy contracts.

The contract contains provider-authored instructional intent only. Learner
responses and private work belong to the consuming local workspace.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any

CONTRACT_VERSION = "1.0"
COGNITIVE_LEVELS = ("knowing", "understanding", "application", "analysis", "independent-production")
ACTIVITY_TYPES = (
    "recitation", "conversation", "seminar", "case", "project", "reflection",
    "guided-observation", "retrieval-practice", "compare-and-contrast", "debate",
    "role-play", "interview", "public-artifact",
)


class PedagogyContractError(ValueError):
    """Raised when provider-authored learning structure is unsafe or malformed."""


def stable_id(kind: str, item: dict[str, Any], index: int = 0) -> str:
    explicit = item.get("id") or item.get(f"{kind}_id")
    if explicit is not None and str(explicit).strip():
        return str(explicit).strip()
    canonical = json.dumps(item, sort_keys=True, separators=(",", ":"))
    return f"dp:{kind}:{hashlib.sha256(canonical.encode()).hexdigest()[:20]}:{index}"


def _strings(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise PedagogyContractError(f"{field_name} must be a list of non-empty strings")
    return [item.strip() for item in value]


@dataclass(frozen=True)
class LearningPromise:
    promise: str = ""
    why_it_matters: str = ""
    outcomes: tuple[dict[str, Any], ...] = ()
    means: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    contract_version: str = CONTRACT_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "promise": self.promise,
            "why_it_matters": self.why_it_matters,
            "outcomes": [dict(item) for item in self.outcomes],
            "means": list(self.means),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class LearningActivity:
    id: str
    title: str
    activity_type: str = "reflection"
    outcome_ids: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    invitation: str = ""
    reading_questions: tuple[str, ...] = ()
    discussion_questions: tuple[str, ...] = ()
    cognitive_level: str = "understanding"
    prerequisites: tuple[str, ...] = ()
    time_minutes: int | None = None
    accessibility_options: tuple[str, ...] = ()
    feedback_mode: str = "formative"
    policy_scopes: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        result = {"id": self.id, "title": self.title, "activity_type": self.activity_type,
                  "outcome_ids": list(self.outcome_ids), "evidence": list(self.evidence),
                  "invitation": self.invitation, "reading_questions": list(self.reading_questions),
                  "discussion_questions": list(self.discussion_questions),
                  "cognitive_level": self.cognitive_level, "prerequisites": list(self.prerequisites),
                  "time_minutes": self.time_minutes, "accessibility_options": list(self.accessibility_options),
                  "feedback_mode": self.feedback_mode, "policy_scopes": list(self.policy_scopes)}
        result.update(self.extra)
        return result


def validate_learning_contract(package: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize optional pedagogy fields without requiring them."""
    if not isinstance(package, dict):
        raise PedagogyContractError("learning package must be an object")
    version = package.get("contract_version", CONTRACT_VERSION)
    if not isinstance(version, str) or not version.startswith("1."):
        raise PedagogyContractError("unsupported pedagogy contract version")
    promise = package.get("promise", {}) or {}
    if isinstance(promise, str):
        promise = {"promise": promise}
    if not isinstance(promise, dict):
        raise PedagogyContractError("promise must be an object or string")
    normalized = dict(package)
    normalized["contract_version"] = version
    for name in ("promise", "why_it_matters"):
        value = promise.get(name, package.get(name, ""))
        if not isinstance(value, str):
            raise PedagogyContractError(f"{name} must be a string")
        normalized[name] = value
    normalized["means"] = _strings(promise.get("means", package.get("means")), "means")
    normalized["evidence"] = _strings(promise.get("evidence", package.get("evidence")), "evidence")
    outcomes = promise.get("outcomes", package.get("outcomes", [])) or []
    if not isinstance(outcomes, list) or any(not isinstance(item, dict) for item in outcomes):
        raise PedagogyContractError("outcomes must be a list of objects")
    seen: set[str] = set()
    normalized["outcomes"] = []
    for index, item in enumerate(outcomes):
        item = dict(item)
        item["id"] = stable_id("outcome", item, index)
        if item["id"] in seen:
            raise PedagogyContractError(f"duplicate outcome identifier: {item['id']}")
        seen.add(item["id"])
        if not isinstance(item.get("title", item.get("description", "")), str):
            raise PedagogyContractError("outcome title must be a string")
        normalized["outcomes"].append(item)
    activities = package.get("activities", []) or []
    if not isinstance(activities, list) or any(not isinstance(item, dict) for item in activities):
        raise PedagogyContractError("activities must be a list of objects")
    normalized["activities"] = []
    for index, raw in enumerate(activities):
        item = dict(raw)
        item["id"] = stable_id("activity", item, index)
        item.setdefault("title", item["id"])
        activity_type = item.get("activity_type", "reflection")
        if activity_type not in ACTIVITY_TYPES:
            raise PedagogyContractError(f"unsupported activity_type: {activity_type}")
        level = item.get("cognitive_level", "understanding")
        if level not in COGNITIVE_LEVELS:
            raise PedagogyContractError(f"unsupported cognitive_level: {level}")
        if "time_minutes" in item and (not isinstance(item["time_minutes"], int) or item["time_minutes"] < 0):
            raise PedagogyContractError("time_minutes must be a non-negative integer")
        for field_name in ("outcome_ids", "prerequisites", "reading_questions", "discussion_questions",
                           "accessibility_options", "policy_scopes", "evidence"):
            item[field_name] = _strings(item.get(field_name), field_name)
        item.setdefault("invitation", "")
        item.setdefault("cognitive_level", "understanding")
        normalized["activities"].append(item)
    return normalized


def render_activity(activity: dict[str, Any]) -> str:
    """Render an inspectable, provider-authored activity for text-first clients."""
    activity = validate_learning_contract({"activities": [activity]})["activities"][0]
    lines = [f"{activity.get('title', activity['id'])} ({activity['activity_type']})"]
    if activity.get("invitation"):
        lines.append(f"Why this matters / invitation: {activity['invitation']}")
    lines.append(f"Cognitive level: {activity['cognitive_level']}")
    lines.append(f"Prerequisites: {', '.join(activity['prerequisites']) or 'none explicit'}")
    if activity.get("time_minutes") is not None:
        lines.append(f"Estimated time: {activity['time_minutes']} minutes")
    if activity.get("reading_questions"):
        lines.append("What to notice: " + " | ".join(activity["reading_questions"]))
    if activity.get("discussion_questions"):
        lines.append("What to discuss: " + " | ".join(activity["discussion_questions"]))
    lines.append("What to do next: produce " + ", ".join(activity["evidence"]) if activity.get("evidence") else "What to do next: complete the activity and record evidence.")
    return "\n".join(lines)


def map_learning_path(package: dict[str, Any]) -> dict[str, Any]:
    """Create a stable, explainable sequence without learner ranking."""
    normalized = validate_learning_contract(package)
    outcomes = {item["id"]: item for item in normalized["outcomes"]}
    steps = []
    for index, activity in enumerate(normalized["activities"]):
        missing = [item for item in activity["prerequisites"]
                   if item not in outcomes and item not in {a["id"] for a in normalized["activities"]}]
        steps.append({"index": index, "activity_id": activity["id"],
                      "outcome_ids": list(activity["outcome_ids"]),
                      "prerequisites": list(activity["prerequisites"]),
                      "missing_prerequisites": missing,
                      "provenance": {"provider": normalized.get("producer", ""), "activity_id": activity["id"]}})
    total = sum(item.get("time_minutes", 0) or 0 for item in normalized["activities"])
    warnings = []
    if total > 600:
        warnings.append({"kind": "workload", "minutes": total, "message": "Review the declared workload."})
    for step in steps:
        if step["missing_prerequisites"]:
            warnings.append({"kind": "missing-prerequisite", "activity_id": step["activity_id"],
                             "items": step["missing_prerequisites"]})
    return {"contract_version": normalized["contract_version"], "steps": steps,
            "workload_minutes": total, "review_prompts": warnings}


def explain_step(package: dict[str, Any], activity_id: str) -> str:
    normalized = validate_learning_contract(package)
    activity = next((item for item in normalized["activities"] if item["id"] == activity_id), None)
    if activity is None:
        raise PedagogyContractError(f"unknown activity: {activity_id}")
    return render_activity(activity)


def record_diagnostic(path_id: str, kind: str, response: str, *, activity_id: str = "",
                     evidence_id: str = "", reviewed: bool = False) -> dict[str, Any]:
    """Create a private learner record; it never changes mastery or policy."""
    if kind not in {"entry", "one-minute", "exit", "reflection"}:
        raise PedagogyContractError("unsupported diagnostic kind")
    if not isinstance(response, str):
        raise PedagogyContractError("diagnostic response must be text")
    record_id = evidence_id or stable_id("evidence", {"path_id": path_id, "kind": kind,
                                                        "activity_id": activity_id, "response": response})
    return {"evidence_id": record_id, "path_id": path_id, "activity_id": activity_id,
            "kind": kind, "status": "reviewed" if reviewed else "draft",
            "private": True, "graded": False, "response": response,
            "provenance": {"source": "learner", "operation": "diagnostic"}}


def export_diagnostics(records: list[dict[str, Any]], *, include_private: bool = False) -> dict[str, Any]:
    """Return an export-safe envelope; response text is excluded by default."""
    exported = []
    redacted = []
    for record in records:
        item = {key: value for key, value in record.items() if key != "response"}
        if include_private:
            item["response"] = record.get("response", "")
        else:
            redacted.append(f"{record.get('evidence_id', 'unknown')}.response")
        exported.append(item)
    return {"schema_version": "1.0", "records": exported,
            "redacted_fields": redacted, "private_content_included": include_private}


def activity_template(activity_type: str, *, title: str, outcome_ids: list[str] | None = None,
                      evidence: list[str] | None = None, debrief: str = "", **metadata: Any) -> dict[str, Any]:
    """Build an inspectable offline activity template with safety metadata."""
    if activity_type not in ACTIVITY_TYPES:
        raise PedagogyContractError(f"unsupported activity_type: {activity_type}")
    if activity_type == "role-play" and not debrief.strip():
        raise PedagogyContractError("role-play activities require a debrief")
    item = {"id": stable_id("activity", {"title": title, "activity_type": activity_type}),
            "title": title, "activity_type": activity_type,
            "outcome_ids": outcome_ids or [], "evidence": evidence or [], "debrief": debrief,
            "participation_modes": metadata.pop("participation_modes", ["written", "spoken"]),
            "consent_required": bool(metadata.pop("consent_required", False)),
            "privacy": metadata.pop("privacy", "local-only"),
            "accessibility_options": metadata.pop("accessibility_options", ["text-only"]),
            "public_release": bool(metadata.pop("public_release", False))}
    item.update(metadata)
    return validate_learning_contract({"activities": [item]})["activities"][0]


def formative_feedback(*, strengths: list[str], problems: list[dict[str, str]], next_step: str,
                       source: str = "deterministic", artifact_id: str = "", activity_id: str = "") -> dict[str, Any]:
    """Return reviewable feedback without editing or rewriting a learner artifact."""
    if source not in {"instructor", "deterministic", "ai"}:
        raise PedagogyContractError("feedback source must be attributable")
    if not isinstance(next_step, str) or not next_step.strip():
        raise PedagogyContractError("feedback requires a concrete next step")
    selected = []
    for problem in problems[:2]:
        if not isinstance(problem, dict) or not problem.get("problem") or not problem.get("why"):
            raise PedagogyContractError("each feedback problem needs problem and why")
        selected.append({"problem": str(problem["problem"]), "why": str(problem["why"]),
                         "prompt": str(problem.get("prompt", "How could you revise this?"))})
    return {"feedback_version": "1.0", "source": source, "artifact_id": artifact_id,
            "activity_id": activity_id, "strengths": [str(item) for item in strengths],
            "problems": selected, "next_step": next_step, "rewrote_artifact": False,
            "review_state": "draft"}


def communication_boundaries(*, participation: str = "Choose a written or spoken response.",
                             privacy: str = "Learner responses stay local unless explicitly exported.",
                             response_limits: str = "This tool provides academic coaching, not counseling.",
                             escalation: str = "Ask the instructor about course requirements; contact local support for personal concerns.") -> str:
    """Render a plain-language boundary notice for accessible learner clients."""
    values = {"Participation": participation, "Privacy": privacy,
              "Response limits": response_limits, "Escalation": escalation}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise PedagogyContractError("communication boundaries must be non-empty text")
    return "\n".join(f"{key}: {value}" for key, value in values.items()) + "\n"


def review_learning_path(package: dict[str, Any]) -> dict[str, Any]:
    """Produce author-facing alignment findings, never a learner score."""
    normalized = validate_learning_contract(package)
    outcome_ids = {item["id"] for item in normalized["outcomes"]}
    linked = {oid for item in normalized["activities"] for oid in item["outcome_ids"]}
    findings = []
    if not normalized["promise"].strip():
        findings.append({"severity": "review", "code": "missing-promise"})
    for oid in sorted(outcome_ids - linked):
        findings.append({"severity": "review", "code": "unlinked-outcome", "id": oid})
    for activity in normalized["activities"]:
        if not activity["evidence"]:
            findings.append({"severity": "review", "code": "missing-evidence", "id": activity["id"]})
        if not activity["accessibility_options"]:
            findings.append({"severity": "review", "code": "missing-accessibility", "id": activity["id"]})
    return {"review_version": "1.0", "status": "ready" if not findings else "needs-review",
            "findings": findings, "learner_labels": [], "engagement_metrics": [],
            "checked": ["promise", "outcomes", "activities", "evidence", "accessibility", "workload"]}


def audit_optional_ai(*, allowed_capabilities: list[str] | None = None,
                      requested_routes: list[str] | None = None,
                      network_enabled: bool = False) -> dict[str, Any]:
    """Audit optional routes; this function never invokes a provider or network."""
    allowed = set(allowed_capabilities or [])
    routes = list(requested_routes or [])
    prohibited = sorted(set(routes) - allowed)
    if not network_enabled and "external-network" in routes:
        prohibited.append("external-network")
    return {"audit_version": "1.0", "provider_invoked": False,
            "network_enabled": network_enabled, "routes": routes,
            "prohibited_routes": sorted(set(prohibited)),
            "fallback": "deterministic-only", "source_grounding_required": True,
            "uncertainty_required": True, "privacy": "local-only-by-default"}
