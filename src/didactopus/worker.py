from __future__ import annotations
import json, tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone
from .repository import update_render_job, register_artifact
from .render_bundle import make_render_bundle

def future_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

def process_render_job(job_id: int, learner_id: str, pack_id: str, fmt: str, fps: int, theme: str, retention_class: str, retention_days: int, animation_payload: dict):
    update_render_job(job_id, status="running")
    try:
        base = Path(tempfile.mkdtemp(prefix=f"didactopus_job_{job_id}_"))
        payload_json = base / "animation_payload.json"
        payload_json.write_text(json.dumps(animation_payload, indent=2), encoding="utf-8")
        out_dir = base / "bundle"
        make_render_bundle(str(payload_json), str(out_dir), fps=fps, fmt=fmt)
        manifest_path = out_dir / "render_manifest.json"
        script_path = out_dir / "render.sh"
        update_render_job(
            job_id,
            status="completed",
            bundle_dir=str(out_dir),
            payload_json=str(payload_json),
            manifest_path=str(manifest_path),
            script_path=str(script_path),
            error_text="",
        )
        register_artifact(
            render_job_id=job_id,
            learner_id=learner_id,
            pack_id=pack_id,
            artifact_type="render_bundle",
            fmt=fmt,
            title=f"{pack_id} animation bundle",
            path=str(out_dir),
            metadata={"fps": fps, "theme": theme, "manifest_path": str(manifest_path), "script_path": str(script_path)},
            retention_class=retention_class,
            expires_at=future_iso(retention_days),
        )
    except Exception as e:
        update_render_job(job_id, status="failed", error_text=str(e))
