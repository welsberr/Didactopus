from pathlib import Path
from datetime import datetime, UTC
import json, shutil
from .review_schema import WorkspaceMeta, WorkspaceRegistry
from .import_validator import preview_draft_pack_import

def utc_now():
    return datetime.now(UTC).isoformat()

class WorkspaceManager:
    def __init__(self, registry_path, default_workspace_root):
        self.registry_path = Path(registry_path)
        self.default_workspace_root = Path(default_workspace_root)
        self.default_workspace_root.mkdir(parents=True, exist_ok=True)

    def load_registry(self):
        if self.registry_path.exists():
            return WorkspaceRegistry.model_validate(json.loads(self.registry_path.read_text(encoding="utf-8")))
        return WorkspaceRegistry()

    def save_registry(self, registry):
        self.registry_path.write_text(registry.model_dump_json(indent=2), encoding="utf-8")

    def list_workspaces(self):
        return self.load_registry()

    def create_workspace(self, workspace_id, title, notes=""):
        registry = self.load_registry()
        workspace_dir = self.default_workspace_root / workspace_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        draft_dir = workspace_dir / "draft_pack"
        draft_dir.mkdir(parents=True, exist_ok=True)
        if not (draft_dir / "pack.yaml").exists():
            (draft_dir / "pack.yaml").write_text(f"name: {workspace_id}\ndisplay_name: {title}\nversion: 0.1.0-draft\n", encoding="utf-8")
        if not (draft_dir / "concepts.yaml").exists():
            (draft_dir / "concepts.yaml").write_text("concepts: []\n", encoding="utf-8")
        meta = WorkspaceMeta(workspace_id=workspace_id, title=title, path=str(workspace_dir), created_at=utc_now(), last_opened_at=utc_now(), notes=notes)
        registry.workspaces = [w for w in registry.workspaces if w.workspace_id != workspace_id] + [meta]
        registry.recent_workspace_ids = [workspace_id] + [w for w in registry.recent_workspace_ids if w != workspace_id]
        self.save_registry(registry)
        return meta

    def touch_recent(self, workspace_id):
        registry = self.load_registry()
        target = None
        for ws in registry.workspaces:
            if ws.workspace_id == workspace_id:
                ws.last_opened_at = utc_now()
                target = ws
                break
        if target is not None:
            registry.recent_workspace_ids = [workspace_id] + [w for w in registry.recent_workspace_ids if w != workspace_id]
            self.save_registry(registry)
        return target

    def get_workspace(self, workspace_id):
        for ws in self.load_registry().workspaces:
            if ws.workspace_id == workspace_id:
                return ws
        return None

    def preview_import(self, source_dir, workspace_id):
        preview = preview_draft_pack_import(source_dir, workspace_id)
        if self.get_workspace(workspace_id) is not None:
            preview.overwrite_required = True
            preview.warnings.append(f"Workspace '{workspace_id}' already exists and import will overwrite draft_pack.")
        return preview

    def import_draft_pack(self, source_dir, workspace_id, title=None, notes="", allow_overwrite=False):
        preview = self.preview_import(source_dir, workspace_id)
        if not preview.ok:
            raise ValueError("Draft pack preview failed: " + "; ".join(preview.errors))
        existing = self.get_workspace(workspace_id)
        if existing is not None and not allow_overwrite:
            raise FileExistsError(f"Workspace '{workspace_id}' already exists; set allow_overwrite to replace its draft pack.")
        meta = existing if existing is not None else self.create_workspace(workspace_id, title or workspace_id, notes=notes)
        if existing is not None:
            self.touch_recent(workspace_id)
        target_draft = Path(meta.path) / "draft_pack"
        if target_draft.exists():
            shutil.rmtree(target_draft)
        shutil.copytree(Path(source_dir), target_draft)
        registry = self.load_registry()
        for ws in registry.workspaces:
            if ws.workspace_id == workspace_id:
                ws.last_opened_at = utc_now()
                if title: ws.title = title
                if notes: ws.notes = notes
                meta = ws
                break
        registry.recent_workspace_ids = [workspace_id] + [w for w in registry.recent_workspace_ids if w != workspace_id]
        self.save_registry(registry)
        return meta
