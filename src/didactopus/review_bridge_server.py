import argparse, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .config import load_config
from .review_bridge import ReviewWorkspaceBridge
from .workspace_manager import WorkspaceManager

def json_response(handler, status, payload):
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)

class ReviewBridgeHandler(BaseHTTPRequestHandler):
    reviewer = "Unknown Reviewer"
    workspace_manager = None
    active_bridge = None
    active_workspace_id = None

    @classmethod
    def set_active_workspace(cls, workspace_id):
        meta = cls.workspace_manager.touch_recent(workspace_id)
        if meta is None: return False
        cls.active_workspace_id = workspace_id
        cls.active_bridge = ReviewWorkspaceBridge(meta.path, reviewer=cls.reviewer)
        return True

    def do_OPTIONS(self): json_response(self, 200, {"ok": True})

    def do_GET(self):
        if self.path == "/api/workspaces":
            return json_response(self, 200, self.workspace_manager.list_workspaces().model_dump())
        if self.path == "/api/load":
            if self.active_bridge is None: return json_response(self, 400, {"error": "no active workspace"})
            return json_response(self, 200, {"workspace_id": self.active_workspace_id, "session": self.active_bridge.load_session().model_dump()})
        return json_response(self, 404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads((self.rfile.read(length) if length else b"{}").decode("utf-8") or "{}")
        if self.path == "/api/workspaces/create":
            meta = self.workspace_manager.create_workspace(payload["workspace_id"], payload["title"], notes=payload.get("notes", ""))
            self.set_active_workspace(meta.workspace_id)
            return json_response(self, 200, {"ok": True, "workspace": meta.model_dump()})
        if self.path == "/api/workspaces/open":
            ok = self.set_active_workspace(payload["workspace_id"])
            return json_response(self, 200 if ok else 404, {"ok": ok, "workspace_id": self.active_workspace_id} if ok else {"error": "workspace not found"})
        if self.path == "/api/workspaces/import-preview":
            return json_response(self, 200, self.workspace_manager.preview_import(payload["source_dir"], payload["workspace_id"]).model_dump())
        if self.path == "/api/workspaces/import":
            try:
                meta = self.workspace_manager.import_draft_pack(payload["source_dir"], payload["workspace_id"], title=payload.get("title"), notes=payload.get("notes",""), allow_overwrite=bool(payload.get("allow_overwrite", False)))
            except FileNotFoundError as exc:
                return json_response(self, 404, {"ok": False, "error": str(exc)})
            except FileExistsError as exc:
                return json_response(self, 409, {"ok": False, "error": str(exc)})
            except ValueError as exc:
                return json_response(self, 400, {"ok": False, "error": str(exc)})
            self.set_active_workspace(meta.workspace_id)
            return json_response(self, 200, {"ok": True, "workspace": meta.model_dump()})
        if self.active_bridge is None:
            return json_response(self, 400, {"error": "no active workspace"})
        if self.path == "/api/save":
            return json_response(self, 200, {"ok": True, "workspace_id": self.active_workspace_id, "session": self.active_bridge.apply_actions(payload.get("actions", [])).model_dump()})
        if self.path == "/api/export":
            session = self.active_bridge.export_promoted()
            return json_response(self, 200, {"ok": True, "promoted_pack_dir": str(self.active_bridge.promoted_pack_dir), "workspace_id": self.active_workspace_id, "session": session.model_dump()})
        return json_response(self, 404, {"error": "not found"})

def build_parser():
    p = argparse.ArgumentParser(description="Didactopus local review bridge server with coverage/alignment QA")
    p.add_argument("--config", default="configs/config.example.yaml")
    return p

def main():
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    ReviewBridgeHandler.reviewer = config.review.default_reviewer
    ReviewBridgeHandler.workspace_manager = WorkspaceManager(config.bridge.registry_path, config.bridge.default_workspace_root)
    server = HTTPServer((config.bridge.host, config.bridge.port), ReviewBridgeHandler)
    print(f"Didactopus review bridge listening on http://{config.bridge.host}:{config.bridge.port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
