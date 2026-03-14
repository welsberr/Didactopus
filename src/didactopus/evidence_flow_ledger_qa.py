import re
from .pack_validator import load_pack_artifacts

def tok(text: str) -> set[str]:
    return {t for t in re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split() if t}

def evidence_flow_ledger_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"ledger_warning_count": 0}}

    arts = loaded["artifacts"]
    concepts = arts["concepts"].get("concepts", []) or []
    roadmap = arts["roadmap"].get("stages", []) or []
    projects = arts["projects"].get("projects", []) or []
    evaluator = arts["evaluator"] or {}
    ledger = arts["mastery_ledger"] or {}

    dimensions = evaluator.get("dimensions", []) or []
    evidence_types = evaluator.get("evidence_types", []) or []
    dimension_mappings = ledger.get("dimension_mappings", {}) or {}
    evidence_mappings = ledger.get("evidence_type_mappings", {}) or {}
    entry_schema = ledger.get("entry_schema", {}) or {}
    confidence_update = ledger.get("confidence_update", {}) or {}

    warnings = []

    dim_names = [d if isinstance(d, str) else d.get("name", "") for d in dimensions]
    ev_names = [e if isinstance(e, str) else e.get("name", "") for e in evidence_types]

    for name in dim_names:
        if name and name not in dimension_mappings:
            warnings.append(f"Evaluator dimension '{name}' has no mastery-ledger mapping.")

    for name in ev_names:
        if name and name not in evidence_mappings:
            warnings.append(f"Evidence type '{name}' has no mastery-ledger entry mapping.")

    route_tokens = set().union(*[tok(x) for x in (dim_names + ev_names)]) if (dim_names or ev_names) else set()
    signal_count = 0
    unrouted_signal_count = 0
    for concept in concepts:
        for signal in concept.get("mastery_signals", []) or []:
            signal_count += 1
            st = tok(signal)
            if st and len(st & route_tokens) == 0:
                unrouted_signal_count += 1
                warnings.append(f"Mastery signal for concept '{concept.get('id')}' has no visible ledger update path via evaluator dimensions or evidence types.")

    checkpoint_tokens = tok(" ".join(str(i) for s in roadmap for i in (s.get("checkpoint", []) or [])))
    deliverable_tokens = tok(" ".join(str(i) for p in projects for i in (p.get("deliverables", []) or [])))
    evidence_tokens = set().union(*[tok(x) for x in ev_names]) if ev_names else set()

    if checkpoint_tokens and evidence_tokens and len(checkpoint_tokens & evidence_tokens) == 0:
        warnings.append("Checkpoint activity has no clear evidence-flow support from declared evidence types.")
    if deliverable_tokens and evidence_tokens and len(deliverable_tokens & evidence_tokens) == 0:
        warnings.append("Project deliverables have no clear evidence-flow support from declared evidence types.")

    required = {"concept_id", "dimension", "score", "confidence", "last_updated"}
    missing = sorted(required - set(entry_schema.keys()))
    if missing:
        warnings.append("Mastery-ledger entry schema is missing required fields: " + ", ".join(missing))
    if "confidence" not in entry_schema or not confidence_update:
        warnings.append("Repeated assessment support for confidence updates appears to be missing.")

    return {
        "warnings": warnings,
        "summary": {
            "ledger_warning_count": len(warnings),
            "dimension_count": len(dim_names),
            "evidence_type_count": len(ev_names),
            "mastery_signal_count": signal_count,
            "unrouted_mastery_signal_count": unrouted_signal_count,
            "ledger_schema_field_count": len(entry_schema),
        },
    }
