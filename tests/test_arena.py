import json
from pathlib import Path

from didactopus.arena import arena_g_evaluation_rows, load_arena_spec, run_didactopus_arena
from didactopus.role_prompts import system_prompt_for_role_variant


def test_system_prompt_for_role_variant_changes_prompt() -> None:
    baseline = system_prompt_for_role_variant("mentor", "baseline")
    strict = system_prompt_for_role_variant("mentor", "strict_grounding")
    trust = system_prompt_for_role_variant("evaluator", "trust_preserving")
    assert baseline != strict
    assert "supplied concept structure" in strict
    assert "preserve learner trust" in trust.lower()


def test_load_arena_spec_reads_candidates() -> None:
    spec = load_arena_spec("configs/arena.example.yaml")
    assert len(spec["candidates"]) == 3
    assert spec["review"]["enabled"] is True
    assert {candidate["language"] for candidate in spec["candidates"]} == {"en", "es", "fr"}


def test_arena_g_evaluation_rows_describe_grounded_behavior() -> None:
    rows = arena_g_evaluation_rows(
        [
            {
                "candidate_name": "local-model",
                "config": "configs/config.example.yaml",
                "prompt_variant": "strict_grounding",
                "language": "en",
                "provider": "stub",
                "role_results": [
                    {
                        "role": "mentor",
                        "model_name": "stub-model",
                        "adequacy_score": 0.91,
                        "adequacy_rating": "adequate",
                        "grounded_score": 0.9,
                        "multilingual_score": 1.0,
                        "latency_ms": 2.5,
                        "response_preview": "Grounded mentor response.",
                    }
                ],
            }
        ]
    )

    assert rows[0]["env"] == "K"
    assert rows[0]["y"] == 1
    assert rows[0]["p"] == 0.91
    assert rows[0]["condition"] == "strict_grounding"
    assert rows[0]["evaluation_target"] == "grounded_role_behavior"


def test_run_didactopus_arena_writes_outputs(tmp_path: Path) -> None:
    payload = run_didactopus_arena(
        arena_spec_path="configs/arena.example.yaml",
        skill_dir="skills/ocw-information-entropy-agent",
        out_dir=tmp_path,
    )
    assert payload["arena"]["name"] == "didactopus-behavior-arena"
    assert len(payload["ranked_candidates"]) == 3
    assert (tmp_path / "arena_results.json").exists()
    assert (tmp_path / "arena_review_queue.json").exists()
    assert (tmp_path / "arena_g_rows.csv").exists()
    assert (tmp_path / "arena_g_manifest.json").exists()
    assert (tmp_path / "arena_g_summary.json").exists()
    assert (tmp_path / "arena_g_summary.md").exists()
    assert (tmp_path / "arena_report.md").exists()
    queue = json.loads((tmp_path / "arena_review_queue.json").read_text(encoding="utf-8"))
    assert queue
    assert payload["ranked_candidates"][0]["language"] in {"en", "es", "fr"}
    assert "multilingual_score" in payload["ranked_candidates"][0]["role_results"][0]
    assert "round_trip" in payload["ranked_candidates"][0]["role_results"][0]
    assert "evaluation_target" in (tmp_path / "arena_g_rows.csv").read_text(encoding="utf-8")
    manifest = json.loads((tmp_path / "arena_g_manifest.json").read_text(encoding="utf-8"))
    assert manifest["evaluation_target"] == "grounded_role_behavior"
    assert manifest["row_file"] == "arena_g_rows.csv"
    summary = json.loads((tmp_path / "arena_g_summary.json").read_text(encoding="utf-8"))
    assert summary["summary_kind"] == "epistemap_g_experiment_summary"
    assert summary["group_by"] == "condition"
    assert summary["manifest"]["experiment_id"] == "didactopus-behavior-arena"
    assert "# Epistemap G Summary" in (tmp_path / "arena_g_summary.md").read_text(encoding="utf-8")
    assert "LLM Review Summary" in (tmp_path / "arena_report.md").read_text(encoding="utf-8")
