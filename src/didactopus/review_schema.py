from pydantic import BaseModel, Field
class WorkspaceMeta(BaseModel):
    workspace_id:str; title:str; path:str; created_at:str; last_opened_at:str; notes:str=""
class WorkspaceRegistry(BaseModel):
    workspaces:list[WorkspaceMeta]=Field(default_factory=list)
    recent_workspace_ids:list[str]=Field(default_factory=list)
class ImportPreview(BaseModel):
    ok:bool=False
    source_dir:str
    workspace_id:str
    overwrite_required:bool=False
    errors:list[str]=Field(default_factory=list)
    warnings:list[str]=Field(default_factory=list)
    summary:dict=Field(default_factory=dict)
    semantic_warnings:list[str]=Field(default_factory=list)
    graph_warnings:list[str]=Field(default_factory=list)
    path_warnings:list[str]=Field(default_factory=list)
    coverage_warnings:list[str]=Field(default_factory=list)
    evaluator_warnings:list[str]=Field(default_factory=list)
