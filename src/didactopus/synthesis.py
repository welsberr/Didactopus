from __future__ import annotations
import json
from .repository import list_packs, create_synthesis_candidate

def _pack_data(pack_row):
    return json.loads(pack_row.data_json or "{}")

def _concepts(pack_row):
    return _pack_data(pack_row).get("concepts", [])

def _norm(text: str) -> set[str]:
    return {t.strip().lower() for t in text.replace("-", " ").replace("_", " ").split() if t.strip()}

def _semantic_similarity(a: dict, b: dict) -> float:
    sa = _norm(a.get("title", "")) | _norm(" ".join(a.get("prerequisites", [])))
    sb = _norm(b.get("title", "")) | _norm(" ".join(b.get("prerequisites", [])))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def _structural_similarity(a: dict, b: dict) -> float:
    pa = set(a.get("prerequisites", []))
    pb = set(b.get("prerequisites", []))
    if not pa and not pb:
        return 0.6
    if not pa or not pb:
        return 0.2
    return len(pa & pb) / len(pa | pb)

def generate_synthesis_candidates(source_pack_id: str | None = None, target_pack_id: str | None = None, limit: int = 20):
    packs = list_packs()
    by_id = {p.id: p for p in packs}
    source_packs = [by_id[source_pack_id]] if source_pack_id and source_pack_id in by_id else packs
    target_packs = [by_id[target_pack_id]] if target_pack_id and target_pack_id in by_id else packs

    created = []
    seen = set()
    for sp in source_packs:
        for tp in target_packs:
            if sp.id == tp.id:
                continue
            for ca in _concepts(sp):
                for cb in _concepts(tp):
                    sem = _semantic_similarity(ca, cb)
                    struct = _structural_similarity(ca, cb)
                    traj = 0.4
                    review_prior = 0.5
                    novelty = 1.0 if (ca.get("id"), cb.get("id")) not in seen else 0.0
                    total = 0.35 * sem + 0.25 * struct + 0.20 * traj + 0.10 * review_prior + 0.10 * novelty
                    if total < 0.45:
                        continue
                    explanation = f"Possible cross-pack overlap between '{ca.get('title')}' and '{cb.get('title')}'."
                    sid = create_synthesis_candidate(
                        source_concept_id=ca.get("id", ""),
                        target_concept_id=cb.get("id", ""),
                        source_pack_id=sp.id,
                        target_pack_id=tp.id,
                        synthesis_kind="cross_pack_similarity",
                        score_semantic=sem,
                        score_structural=struct,
                        score_trajectory=traj,
                        score_review_history=review_prior,
                        explanation=explanation,
                        evidence={"novelty": novelty, "source_title": ca.get("title"), "target_title": cb.get("title")},
                    )
                    seen.add((ca.get("id"), cb.get("id")))
                    created.append(sid)
                    if len(created) >= limit:
                        return created
    return created
