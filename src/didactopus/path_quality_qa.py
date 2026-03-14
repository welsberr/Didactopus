import re
from statistics import mean
from .pack_validator import load_pack_artifacts

CAPSTONE_HINTS = {"capstone","final","comprehensive","culminating"}

def tokenize(text: str) -> set[str]:
    return {t for t in re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split() if t}

def path_quality_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"path_warning_count": 0}}
    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    roadmap = loaded["artifacts"]["roadmap"].get("stages", []) or []
    projects = loaded["artifacts"]["projects"].get("projects", []) or []
    concept_by_id = {c.get("id"): c for c in concepts if c.get("id")}
    project_prereq_ids = {cid for p in projects for cid in (p.get("prerequisites", []) or [])}
    warnings = []; stage_sizes = []; stage_prereq_loads = []; assessed = set(project_prereq_ids)
    for idx, stage in enumerate(roadmap):
        sc = stage.get("concepts", []) or []; cp = stage.get("checkpoint", []) or []
        stage_sizes.append(len(sc))
        if len(sc) == 0: warnings.append(f"Roadmap stage '{stage.get('title', idx)}' has no concepts.")
        if len(cp) == 0: warnings.append(f"Roadmap stage '{stage.get('title', idx)}' has no checkpoint activity.")
        cp_tokens = tokenize(' '.join(str(x) for x in cp))
        for cid in sc:
            if tokenize(concept_by_id.get(cid, {}).get("title","")) & cp_tokens:
                assessed.add(cid)
        stage_prereq_loads.append(sum(len(concept_by_id.get(cid, {}).get("prerequisites", []) or []) for cid in sc))
    for cid in concept_by_id:
        if cid not in assessed: warnings.append(f"Concept '{cid}' is not visibly assessed by checkpoints or project prerequisites.")
    for idx, project in enumerate(projects):
        if tokenize(project.get("title","")) & CAPSTONE_HINTS and len(roadmap) >= 3 and idx == 0:
            warnings.append(f"Project '{project.get('title')}' looks capstone-like but appears very early in the project list.")
    if roadmap:
        for idx in range(max(0, len(roadmap)-2), len(roadmap)):
            stage = roadmap[idx]; sc = stage.get("concepts", []) or []; cp = stage.get("checkpoint", []) or []
            linked = any(cid in project_prereq_ids for cid in sc)
            if sc and len(cp) == 0 and not linked:
                warnings.append(f"Late roadmap stage '{stage.get('title', idx)}' may be a dead end: no checkpoints and no project linkage.")
    if stage_sizes:
        avg = mean(stage_sizes)
        for idx, size in enumerate(stage_sizes):
            title = roadmap[idx].get("title", idx)
            if avg > 0 and size >= max(4, 2.5 * avg): warnings.append(f"Roadmap stage '{title}' is unusually large relative to other stages.")
            if len(roadmap) >= 3 and size == 1: warnings.append(f"Roadmap stage '{title}' is unusually small and may need merging or support concepts.")
    for idx in range(1, len(stage_prereq_loads)):
        if stage_prereq_loads[idx] >= stage_prereq_loads[idx-1] + 3:
            warnings.append(f"Roadmap stage '{roadmap[idx].get('title', idx)}' shows an abrupt prerequisite-load jump from the prior stage.")
    return {"warnings": warnings, "summary": {"path_warning_count": len(warnings)}}
