from __future__ import annotations
from pathlib import Path
import re
from difflib import SequenceMatcher
from .pack_validator import load_pack_artifacts

BROAD_HINTS = {"and", "overview", "foundations", "introduction", "basics", "advanced"}

def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()

def token_set(text: str) -> set[str]:
    return {t for t in normalize_title(text).split() if t}

def semantic_qa_for_pack(source_dir: str | Path) -> dict:
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"semantic_warning_count": 0}}

    pack = loaded["artifacts"]["pack"]
    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    roadmap = loaded["artifacts"]["roadmap"].get("stages", []) or []

    warnings: list[str] = []

    # Near-duplicate titles
    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            a = concepts[i]
            b = concepts[j]
            sim = similarity(a.get("title", ""), b.get("title", ""))
            if sim >= 0.86 and a.get("id") != b.get("id"):
                warnings.append(f"Near-duplicate concept titles: '{a.get('title')}' vs '{b.get('title')}'")

    # Over-broad titles
    for concept in concepts:
        title = concept.get("title", "")
        toks = token_set(title)
        if len(toks) >= 3 and (BROAD_HINTS & toks):
            warnings.append(f"Concept '{title}' may be over-broad and may need splitting.")
        if " and " in title.lower():
            warnings.append(f"Concept '{title}' is compound and may combine multiple ideas.")

    # Similar descriptions
    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            da = str(concepts[i].get("description", "") or "")
            db = str(concepts[j].get("description", "") or "")
            if len(da) > 20 and len(db) > 20:
                sim = SequenceMatcher(None, da.lower(), db.lower()).ratio()
                if sim >= 0.82:
                    warnings.append(
                        f"Concept descriptions are very similar: '{concepts[i].get('title')}' vs '{concepts[j].get('title')}'"
                    )

    # Thin prerequisite chains on advanced-sounding concepts
    for concept in concepts:
        title = normalize_title(concept.get("title", ""))
        prereqs = concept.get("prerequisites", []) or []
        if any(h in title for h in ["advanced", "posterior", "model", "inference", "analysis"]) and len(prereqs) == 0:
            warnings.append(f"Concept '{concept.get('title')}' looks advanced but has no prerequisites.")

    # Missing bridge concepts between roadmap stages
    concept_by_id = {c.get("id"): c for c in concepts if c.get("id")}
    for idx in range(len(roadmap) - 1):
        current_stage = roadmap[idx]
        next_stage = roadmap[idx + 1]
        current_titles = [concept_by_id[cid].get("title", "") for cid in current_stage.get("concepts", []) if cid in concept_by_id]
        next_titles = [concept_by_id[cid].get("title", "") for cid in next_stage.get("concepts", []) if cid in concept_by_id]
        current_tokens = set().union(*[token_set(t) for t in current_titles]) if current_titles else set()
        next_tokens = set().union(*[token_set(t) for t in next_titles]) if next_titles else set()
        overlap = current_tokens & next_tokens
        if current_titles and next_titles and len(overlap) == 0:
            warnings.append(
                f"Roadmap transition from stage '{current_stage.get('title')}' to '{next_stage.get('title')}' may lack a bridge concept."
            )
        if len(next_titles) == 1 and len(current_titles) >= 2 and len(overlap) == 0:
            warnings.append(
                f"Stage '{next_stage.get('title')}' contains a singleton concept with weak visible continuity from the prior stage."
            )

    return {
        "warnings": warnings,
        "summary": {
            "semantic_warning_count": len(warnings),
            "pack_name": pack.get("name", ""),
        },
    }
