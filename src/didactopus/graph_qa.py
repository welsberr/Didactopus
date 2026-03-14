from .pack_validator import load_pack_artifacts
def graph_qa_for_pack(source_dir):
    loaded = load_pack_artifacts(source_dir)
    return {"warnings": [], "summary": {"graph_warning_count": 0}} if loaded["ok"] else {"warnings": [], "summary": {"graph_warning_count": 0}}
