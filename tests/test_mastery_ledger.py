from pathlib import Path
import json

from didactopus.agentic_loop import run_demo_agentic_loop
from didactopus.mastery_ledger import (
    build_capability_profile,
    export_capability_profile_json,
    export_capability_report_markdown,
    export_artifact_manifest,
)


def test_build_capability_profile() -> None:
    state = run_demo_agentic_loop([
        "foundations-statistics::descriptive-statistics",
        "bayes-extension::prior",
    ])
    profile = build_capability_profile(state, "Bayesian inference")
    assert profile.domain == "Bayesian inference"
    assert len(profile.artifacts) == 2


def test_exports(tmp_path: Path) -> None:
    state = run_demo_agentic_loop([
        "foundations-statistics::descriptive-statistics",
        "bayes-extension::prior",
    ])
    profile = build_capability_profile(state, "Bayesian inference")

    json_path = tmp_path / "capability_profile.json"
    md_path = tmp_path / "capability_report.md"
    manifest_path = tmp_path / "artifact_manifest.json"

    export_capability_profile_json(profile, str(json_path))
    export_capability_report_markdown(profile, str(md_path))
    export_artifact_manifest(profile, str(manifest_path))

    assert json_path.exists()
    assert md_path.exists()
    assert manifest_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["domain"] == "Bayesian inference"
