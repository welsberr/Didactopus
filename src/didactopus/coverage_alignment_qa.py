import re
from .pack_validator import load_pack_artifacts

def tokenize(text: str) -> set[str]:
    return {t for t in re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split() if t}

def _concept_title_tokens(title: str) -> set[str]:
    stop = {"the","of","and","to","for","in","on","a","an"}
    return {t for t in tokenize(title) if t not in stop}

def coverage_alignment_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"coverage_warning_count": 0}}
    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    roadmap = loaded["artifacts"]["roadmap"].get("stages", []) or []
    projects = loaded["artifacts"]["projects"].get("projects", []) or []
    rubrics = loaded["artifacts"]["rubrics"].get("rubrics", []) or []

    concept_by_id = {c.get("id"): c for c in concepts if c.get("id")}
    roadmap_ids = {cid for stage in roadmap for cid in (stage.get("concepts", []) or [])}
    checkpoint_tokens = tokenize(" ".join(str(item) for stage in roadmap for item in (stage.get("checkpoint", []) or [])))
    project_ids = {cid for project in projects for cid in (project.get("prerequisites", []) or [])}
    deliverable_tokens = tokenize(" ".join(str(item) for project in projects for item in (project.get("deliverables", []) or [])))

    checkpoint_ids = set()
    assessed_ids = set(project_ids)
    warnings = []

    for cid, concept in concept_by_id.items():
        title_tokens = _concept_title_tokens(concept.get("title", ""))
        if cid not in roadmap_ids:
            warnings.append(f"Concept '{cid}' does not appear in any roadmap stage.")
        if title_tokens and (title_tokens & checkpoint_tokens):
            checkpoint_ids.add(cid)
        else:
            warnings.append(f"Concept '{cid}' is not reflected in checkpoint language.")
        if cid not in project_ids:
            warnings.append(f"Concept '{cid}' is not referenced by any project prerequisites.")
        if cid in project_ids or cid in checkpoint_ids:
            assessed_ids.add(cid)
        else:
            warnings.append(f"Concept '{cid}' is never covered by checkpoints or projects.")

    for cid, concept in concept_by_id.items():
        for signal in concept.get("mastery_signals", []) or []:
            signal_tokens = tokenize(signal)
            if signal_tokens and not ((signal_tokens & checkpoint_tokens) or (signal_tokens & deliverable_tokens)):
                warnings.append(f"Mastery signal for concept '{cid}' is not reflected in checkpoints or project deliverables.")

    rubric_tokens = set()
    for rubric in rubrics:
        for criterion in rubric.get("criteria", []) or []:
            rubric_tokens |= tokenize(criterion)

    project_and_signal_tokens = set(deliverable_tokens)
    for concept in concept_by_id.values():
        for signal in concept.get("mastery_signals", []) or []:
            project_and_signal_tokens |= tokenize(signal)

    if rubric_tokens and len(rubric_tokens & project_and_signal_tokens) == 0:
        warnings.append("Rubric criteria show weak lexical overlap with mastery signals and project deliverables.")

    concept_count = max(1, len(concept_by_id))
    if projects and len(project_ids) <= max(1, concept_count // 4):
        warnings.append("Projects appear to cover only a narrow subset of the concept set.")

    return {
        "warnings": warnings,
        "summary": {
            "coverage_warning_count": len(warnings),
            "concept_count": len(concept_by_id),
            "roadmap_covered_count": len(roadmap_ids & set(concept_by_id)),
            "checkpoint_covered_count": len(checkpoint_ids),
            "project_covered_count": len(project_ids & set(concept_by_id)),
            "assessed_concept_count": len(assessed_ids),
        },
    }
