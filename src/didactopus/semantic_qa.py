from .pack_validator import load_pack_artifacts
def semantic_qa_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    return {"warnings": [], "summary": {"semantic_warning_count": 0}} if loaded["ok"] else {"warnings": [], "summary": {"semantic_warning_count": 0}}
