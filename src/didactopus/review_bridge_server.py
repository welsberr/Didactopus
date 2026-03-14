from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from .config import load_config
from .review_bridge import ReviewWorkspaceBridge
from .workspace_manager import WorkspaceManager

def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
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
    reviewer: str = "Unknown Reviewer"
    workspace_manager: WorkspaceManager = None  # type: ignore
    active_bridge: ReviewWorkspaceBridge | None = None
    active_workspace_id: str | None = None

    @classmethod
    def set_active_workspace(cls, workspace_id: str) -> bool:
        meta = cls.workspace_manager.touch_recent(workspace_id)
        if meta is None:
            return False
        cls.active_workspace_id = workspace_id
        cls.active_bridge = ReviewWorkspaceBridge(meta.path, reviewer=cls.reviewer)
        return True

    def do_OPTIONS(self):
        json_response(self, 200, {"ok": True})

    def do_GET(self):
        if self.path == "/api/workspaces":
            reg = self.workspace_manager.list_workspaces()
            json_response(self, 200, reg.model_dump())
            return
        if self.path == "/api/load":
            if self.active_bridge is None:
                json_response(self, 400, {"error": "no active workspace"})
                return
            session = self.active_bridge.load_session()
            json_response(self, 200, {"workspace_id": self.active_workspace_id, "session": session.model_dump()})
            return
        json_response(self, 404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        payload = json.loads(raw.decode("utf-8") or "{}")

        if self.path == "/api/workspaces/create":
            meta = self.workspace_manager.create_workspace(
                workspace_id=payload["workspace_id"],
                title=payload["title"],
                notes=payload.get("notes", "")
            )
            self.set_active_workspace(meta.workspace_id)
            json_response(self, 200, {"ok": True, "workspace": meta.model_dump()})
            return

        if self.path == "/api/workspaces/open":
            ok = self.set_active_workspace(payload["workspace_id"])
            if not ok:
                json_response(self, 404, {"error": "workspace not found"})
                return
            json_response(self, 200, {"ok": True, "workspace_id": self.active_workspace_id})
            return

        if self.path == "/api/workspaces/import-preview":
            preview = self.workspace_manager.preview_import(
                source_dir=payload["source_dir"],
                workspace_id=payload["workspace_id"]
            )
            json_response(self, 200, preview.model_dump())
            return

        if self.path == "/api/workspaces/import":
            try:
                meta = self.workspace_manager.import_draft_pack(
                    source_dir=payload["source_dir"],
                    workspace_id=payload["workspace_id"],
                    title=payload.get("title"),
                    notes=payload.get("notes", ""),
                    allow_overwrite=bool(payload.get("allow_overwrite", False)),
                )
            except FileNotFoundError as exc:
                json_response(self, 404, {"ok": False, "error": str(exc)})
                return
            except FileExistsError as exc:
                json_response(self, 409, {"ok": False, "error": str(exc)})
                return
            except ValueError as exc:
                json_response(self, 400, {"ok": False, "error": str(exc)})
                return
            self.set_active_workspace(meta.workspace_id)
            json_response(self, 200, {"ok": True, "workspace": meta.model_dump()})
            return

        if self.active_bridge is None:
            json_response(self, 400, {"error": "no active workspace"})
            return

        if self.path == "/api/save":
            session = self.active_bridge.apply_actions(payload.get("actions", []))
            json_response(self, 200, {"ok": True, "workspace_id": self.active_workspace_id, "session": session.model_dump()})
            return

        if self.path == "/api/export":
            session = self.active_bridge.export_promoted()
            json_response(self, 200, {"ok": True, "promoted_pack_dir": str(self.active_bridge.promoted_pack_dir), "workspace_id": self.active_workspace_id, "session": session.model_dump()})
            return

        json_response(self, 404, {"error": "not found"})

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus local review bridge server with graph QA")
    parser.add_argument("--config", default="configs/config.example.yaml")
    return parser

def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    ReviewBridgeHandler.reviewer = config.review.default_reviewer
    ReviewBridgeHandler.workspace_manager = WorkspaceManager(
        registry_path=config.bridge.registry_path,
        default_workspace_root=config.bridge.default_workspace_root
    )
    server = HTTPServer((config.bridge.host, config.bridge.port), ReviewBridgeHandler)
    print(f"Didactopus review bridge listening on http://{config.bridge.host}:{config.bridge.port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
