from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile


def validate_notebook_learner_run(payload: dict) -> dict:
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported learner run schema version.")
    if payload.get("run_kind") != "notebook_sequence":
        raise ValueError("Persisted payload is not a notebook sequence learner run.")
    if not payload.get("run_id"):
        raise ValueError("Persisted learner run has no run_id.")
    if not payload.get("learner_id"):
        raise ValueError("Persisted learner run has no learner_id.")
    if not payload.get("study_plan", {}).get("sequence_id"):
        raise ValueError("Persisted learner run has no sequence_id.")
    if not isinstance(payload.get("learner_evidence"), list):
        raise ValueError("Persisted learner run has no learner_evidence list.")
    return payload


def load_notebook_learner_run(path: str | Path) -> dict:
    resolved_path = Path(path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Learner run state does not exist: {resolved_path}")
    payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Persisted learner run must be a JSON object.")
    return validate_notebook_learner_run(payload)


def save_notebook_learner_run(
    path: str | Path,
    payload: dict,
    *,
    overwrite: bool = False,
) -> Path:
    resolved_path = Path(path)
    if resolved_path.exists() and not overwrite:
        raise FileExistsError(
            f"Learner run state already exists: {resolved_path}. Resume it explicitly to append."
        )
    validate_notebook_learner_run(payload)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=resolved_path.parent,
            prefix=f".{resolved_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, resolved_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return resolved_path
