from __future__ import annotations

import hashlib
import json
from pathlib import Path

from didactopus.interoperability import (
    PackCapsuleManifest,
    build_interoperability_registry,
    registry_payload,
    validate_pack_capsule,
)


def _write_capsule(tmp_path: Path, *, sha256: str | None = None, remote_routes_allowed: bool = False) -> Path:
    content_path = tmp_path / "lesson.md"
    content_path.write_text("# Lesson\n\nA short reviewed lesson.\n", encoding="utf-8")
    digest = sha256 or hashlib.sha256(content_path.read_bytes()).hexdigest()
    manifest = {
        "capsule_id": "capsule-example-v0",
        "pack_name": "example-foundations",
        "title": "Example Foundations",
        "version": "0.1.0",
        "language": "en",
        "license": "CC-BY-4.0",
        "review_status": "reviewed",
        "content_files": [
            {
                "path": "lesson.md",
                "role": "source",
                "sha256": digest,
                "media_type": "text/markdown",
            }
        ],
        "provenance_summary": "Synthetic fixture for pack capsule validation.",
        "accessibility_features": ["text_only"],
        "model_requirements": [
            {
                "role": "mentor",
                "minimum_context_tokens": 4096,
                "tested_routes": ["stub-local"],
            }
        ],
        "external_adapters": [
            {
                "standard_id": "qti",
                "direction": "export",
                "mapping_status": "lossy_export",
                "notes": "Reviewed quiz export candidate.",
            }
        ],
        "privacy_profile": "local_only",
        "telemetry_enabled": False,
        "remote_routes_allowed": remote_routes_allowed,
    }
    manifest_path = tmp_path / "didactopus-pack-capsule.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def test_registry_crosswalk_targets_are_known() -> None:
    registry = build_interoperability_registry()

    assert not registry.validate_crosswalk_targets()
    assert "qti" in registry.standards_by_id()
    assert any(crosswalk.external_standard_id == "xapi" for crosswalk in registry.crosswalks)


def test_registry_payload_contains_policy_and_validation() -> None:
    payload = registry_payload()

    assert payload["validation"]["ok"] is True
    assert payload["default_policy"]["canonical_internal_format"] == "Didactopus pack capsule"


def test_pack_capsule_manifest_rejects_remote_routes_for_local_only() -> None:
    data = {
        "capsule_id": "bad-local",
        "pack_name": "bad",
        "title": "Bad",
        "version": "0.1.0",
        "license": "CC-BY-4.0",
        "review_status": "draft",
        "content_files": [{"path": "lesson.md", "role": "source"}],
        "provenance_summary": "Fixture.",
        "privacy_profile": "local_only",
        "remote_routes_allowed": True,
    }

    try:
        PackCapsuleManifest.model_validate(data)
    except ValueError as exc:
        assert "remote routes" in str(exc)
    else:
        raise AssertionError("Expected local_only remote route validation failure")


def test_validate_pack_capsule_accepts_valid_manifest(tmp_path: Path) -> None:
    manifest_path = _write_capsule(tmp_path)

    result = validate_pack_capsule(manifest_path)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["summary"]["pack_name"] == "example-foundations"


def test_validate_pack_capsule_reports_checksum_mismatch(tmp_path: Path) -> None:
    manifest_path = _write_capsule(tmp_path, sha256="0" * 64)

    result = validate_pack_capsule(manifest_path)

    assert result["ok"] is False
    assert any("Checksum mismatch" in error for error in result["errors"])
