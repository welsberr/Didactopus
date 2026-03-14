from __future__ import annotations

def format_recommendation_card(item: dict) -> dict:
    title = item.get("title", item.get("concept_id", "Next concept"))
    reason = item.get("reason", "Good next step.")
    return {
        "title": title,
        "subtitle": "Recommended next step",
        "body": reason,
        "cta": f"Work on {title}",
    }

def format_reward_message(kind: str, label: str) -> str:
    if kind == "unlock":
        return f"Unlocked: {label}"
    if kind == "milestone":
        return f"Milestone reached: {label}"
    if kind == "capstone":
        return f"Capstone-ready: {label}"
    return f"Progress recorded: {label}"
