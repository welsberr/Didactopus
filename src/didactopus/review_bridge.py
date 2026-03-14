from __future__ import annotations
from pathlib import Path
import json
from .review_loader import load_draft_pack
from .review_schema import ReviewSession, ReviewAction
from .review_actions import apply_action
from .review_export import export_review_state_json, export_promoted_pack

class ReviewWorkspaceBridge:
    def __init__(self, workspace_dir: str | Path, reviewer: str = "Unknown Reviewer") -> None:
        self.workspace_dir = Path(workspace_dir); self.reviewer = reviewer; self.workspace_dir.mkdir(parents=True, exist_ok=True)
    @property
    def draft_pack_dir(self) -> Path: return self.workspace_dir / "draft_pack"
    @property
    def review_session_path(self) -> Path: return self.workspace_dir / "review_session.json"
    @property
    def promoted_pack_dir(self) -> Path: return self.workspace_dir / "promoted_pack"
    def load_session(self) -> ReviewSession:
        if self.review_session_path.exists():
            return ReviewSession.model_validate(json.loads(self.review_session_path.read_text(encoding="utf-8")))
        draft = load_draft_pack(self.draft_pack_dir)
        session = ReviewSession(reviewer=self.reviewer, draft_pack=draft)
        export_review_state_json(session, self.review_session_path)
        return session
    def save_session(self, session: ReviewSession) -> None:
        export_review_state_json(session, self.review_session_path)
    def apply_actions(self, actions: list[dict]) -> ReviewSession:
        session = self.load_session()
        for action_dict in actions:
            apply_action(session, session.reviewer, ReviewAction.model_validate(action_dict))
        self.save_session(session); return session
    def export_promoted(self) -> ReviewSession:
        session = self.load_session(); export_promoted_pack(session, self.promoted_pack_dir); return session
