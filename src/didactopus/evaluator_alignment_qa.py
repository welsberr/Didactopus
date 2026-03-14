import re
from .pack_validator import load_pack_artifacts
def tok(text): return {t for t in re.sub(r"[^a-z0-9]+"," ",str(text).lower()).split() if t}
def evaluator_alignment_for_pack(source_dir):
    loaded=load_pack_artifacts(source_dir)
    if not loaded["ok"]: return {"warnings":[],"summary":{"evaluator_warning_count":0}}
    arts=loaded["artifacts"]
    concepts=arts["concepts"].get("concepts",[]) or []
    roadmap=arts["roadmap"].get("stages",[]) or []
    projects=arts["projects"].get("projects",[]) or []
    rubrics=arts["rubrics"].get("rubrics",[]) or []
    evaluator=arts["evaluator"] or {}
    dims=evaluator.get("dimensions",[]) or []
    evidence=evaluator.get("evidence_types",[]) or []
    checkpoint_tokens=tok(" ".join(str(i) for s in roadmap for i in (s.get("checkpoint",[]) or [])))
    deliverable_tokens=tok(" ".join(str(i) for p in projects for i in (p.get("deliverables",[]) or [])))
    rubric_tokens=set()
    for r in rubrics:
        for c in (r.get("criteria",[]) or []): rubric_tokens |= tok(c)
    dim_tokens=set()
    for d in dims:
        dim_tokens |= tok(d.get("name","")) | tok(d.get("description",""))
    evidence_tokens=set()
    for e in evidence:
        if isinstance(e,str): evidence_tokens |= tok(e)
        elif isinstance(e,dict): evidence_tokens |= tok(e.get("name","")) | tok(e.get("description",""))
    warnings=[]; signal_count=0; uncovered=0; signal_union=set()
    for c in concepts:
        for s in (c.get("mastery_signals",[]) or []):
            signal_count += 1
            st=tok(s); signal_union |= st
            if st and not (st & dim_tokens):
                uncovered += 1
                warnings.append(f"Mastery signal for concept '{c.get('id')}' has no visible evaluator-dimension coverage.")
    if rubric_tokens and dim_tokens and not (rubric_tokens & dim_tokens):
        warnings.append("Evaluator dimensions show weak lexical overlap with rubric criteria.")
        warnings.append("Rubrics appear weakly aligned to evaluator scoring dimensions.")
    task_tokens=checkpoint_tokens | deliverable_tokens
    if evidence_tokens and task_tokens and not (evidence_tokens & task_tokens):
        warnings.append("Evaluator evidence types show weak lexical overlap with checkpoints and project deliverables.")
    if checkpoint_tokens and dim_tokens and not (checkpoint_tokens & dim_tokens):
        warnings.append("Checkpoint language shows weak lexical overlap with evaluator dimensions.")
    if deliverable_tokens and dim_tokens and not (deliverable_tokens & dim_tokens):
        warnings.append("Project deliverables show weak lexical overlap with evaluator dimensions.")
    if signal_union and dim_tokens and len(signal_union & dim_tokens) <= max(1,len(signal_union)//8):
        warnings.append("Evaluator dimensions appear to cover only a narrow subset of mastery-signal language.")
    return {"warnings":warnings,"summary":{"evaluator_warning_count":len(warnings),"dimension_count":len(dims),"evidence_type_count":len(evidence),"mastery_signal_count":signal_count,"uncovered_mastery_signal_count":uncovered}}
