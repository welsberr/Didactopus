from __future__ import annotations
from pathlib import Path
import json
from .models import PackData, LearnerState

class FileStorage:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.packs_dir = self.base_dir / "packs"
        self.learners_dir = self.base_dir / "learners"
        self.packs_dir.mkdir(parents=True, exist_ok=True)
        self.learners_dir.mkdir(parents=True, exist_ok=True)

    def list_packs(self) -> list[PackData]:
        out = []
        for path in sorted(self.packs_dir.glob("*.json")):
            out.append(PackData.model_validate_json(path.read_text(encoding="utf-8")))
        return out

    def get_pack(self, pack_id: str) -> PackData | None:
        path = self.packs_dir / f"{pack_id}.json"
        if not path.exists():
            return None
        return PackData.model_validate_json(path.read_text(encoding="utf-8"))

    def get_learner_state(self, learner_id: str) -> LearnerState:
        path = self.learners_dir / f"{learner_id}.json"
        if not path.exists():
            return LearnerState(learner_id=learner_id)
        return LearnerState.model_validate_json(path.read_text(encoding="utf-8"))

    def save_learner_state(self, state: LearnerState) -> LearnerState:
        path = self.learners_dir / f"{state.learner_id}.json"
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return state
