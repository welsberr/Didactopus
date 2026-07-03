from __future__ import annotations

from pathlib import Path

from didactopus import groundrecall_pack_bridge as bridge_module


def test_run_doclift_bundle_with_groundrecall_bridges_export_and_demo(monkeypatch, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_export(store_dir, concept_ref, out_dir):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = out_dir / "groundrecall_query_bundle.json"
        bundle_path.write_text("{}", encoding="utf-8")
        sidecar_path = out_dir / "bayesian_reliability.md"
        sidecar_path.write_text("# Epistemap Bayesian Reliability\n", encoding="utf-8")
        captured["store_dir"] = str(store_dir)
        captured["concept_ref"] = concept_ref
        captured["export_dir"] = str(out_dir)
        return {
            "bundle_path": str(bundle_path),
            "bayesian_reliability_markdown_path": str(sidecar_path),
            "bundle": {"bundle_kind": "groundrecall_query_bundle"},
        }

    def _fake_run_doclift_bundle_demo(**kwargs):
        captured["demo_kwargs"] = kwargs
        pack_dir = Path(kwargs["pack_dir"])
        pack_dir.mkdir(parents=True, exist_ok=True)
        (pack_dir / "pack.yaml").write_text("supporting_artifacts:\n- groundrecall_query_bundle.json\n", encoding="utf-8")
        return {"pack_dir": str(kwargs["pack_dir"]), "groundrecall_bundle_included": True}

    monkeypatch.setattr(bridge_module, "_load_groundrecall_export", lambda: _fake_export)
    monkeypatch.setattr(bridge_module, "run_doclift_bundle_demo", _fake_run_doclift_bundle_demo)

    payload = bridge_module.run_doclift_bundle_with_groundrecall(
        groundrecall_store_dir=tmp_path / "store",
        groundrecall_concept_ref="channel-capacity",
        bundle_dir=tmp_path / "bundle",
        course_title="Example Course",
        pack_dir=tmp_path / "pack",
    )

    assert captured["concept_ref"] == "channel-capacity"
    assert captured["demo_kwargs"]["groundrecall_query_bundle_path"].endswith("groundrecall_query_bundle.json")
    assert payload["groundrecall_concept_ref"] == "channel-capacity"
    assert payload["groundrecall_query_bundle_path"].endswith("groundrecall_query_bundle.json")
    assert payload["bayesian_reliability_markdown_path"].endswith("bayesian_reliability.md")
    assert (tmp_path / "pack" / "bayesian_reliability.md").exists()
    assert "bayesian_reliability.md" in (tmp_path / "pack" / "pack.yaml").read_text(encoding="utf-8")
