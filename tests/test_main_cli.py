import json
import sys
from pathlib import Path

import pytest

from didactopus import main as didactopus_main


def test_main_provider_inspect_subcommand(capsys) -> None:
    root = Path(__file__).resolve().parents[1]
    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "provider-inspect",
            "--config",
            str(root / "configs" / "config.example.yaml"),
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    output = capsys.readouterr().out
    assert '"provider": "stub"' in output
    assert '"kind": "chat"' in output


def test_main_legacy_review_invocation_routes_to_review(monkeypatch) -> None:
    original_argv = sys.argv
    seen: dict[str, object] = {}

    def fake_run_review(args) -> None:
        seen["command"] = args.command
        seen["draft_pack"] = args.draft_pack
        seen["config"] = args.config

    monkeypatch.setattr(didactopus_main, "_run_review", fake_run_review)
    try:
        sys.argv = [
            "didactopus.main",
            "--draft-pack",
            "demo-pack",
            "--config",
            "configs/config.example.yaml",
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    assert seen == {
        "command": "review",
        "draft_pack": "demo-pack",
        "config": "configs/config.example.yaml",
    }


def test_main_citegeist_okf_source_corpus_command(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "citegeist-okf"
    out_dir = tmp_path / "didactopus-source"
    (bundle / "works").mkdir(parents=True)
    (bundle / "manifest.json").write_text(
        """
{
  "bundle_kind": "citegeist_okf_bundle",
  "topic": {"name": "Graph Methods"},
  "paths": {"works": {"smith2024graphs": "works/smith2024graphs.md"}}
}
""".strip(),
        encoding="utf-8",
    )
    (bundle / "works" / "smith2024graphs.md").write_text(
        "\n".join(
            [
                "---",
                'okf_type: "citegeist.work"',
                'citation_key: "smith2024graphs"',
                'entry_type: "article"',
                'title: "Graph-first bibliography augmentation"',
                'year: "2024"',
                "authors:",
                '  - "Smith, Jane"',
                "topic_slugs:",
                '  - "graph-methods"',
                "---",
                "# Graph-first bibliography augmentation",
                "",
                "## Abstract",
                "",
                "We study citation graphs for literature discovery.",
            ]
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "citegeist-okf-source-corpus",
            str(bundle),
            str(out_dir),
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    output = capsys.readouterr().out
    assert "source_corpus_path" in output
    source_corpus = json.loads((out_dir / "source_corpus.json").read_text(encoding="utf-8"))
    resources = (out_dir / "resources.md").read_text(encoding="utf-8")
    assert source_corpus["course_title"] == "Graph Methods"
    assert source_corpus["sources"][0]["metadata"]["citation_key"] == "smith2024graphs"
    assert any(fragment["kind"] == "abstract" for fragment in source_corpus["fragments"])
    assert "`smith2024graphs`" in resources


def test_main_ingest_ensemble_command(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    out_dir = tmp_path / "ensemble-out"
    source.mkdir()
    (source / "lesson.md").write_text(
        "# Lesson\n\n- A claim because the source states it.\n",
        encoding="utf-8",
    )

    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "ingest-ensemble",
            str(source),
            "--out-dir",
            str(out_dir),
            "--ingest-id",
            "main-cli-ensemble",
            "--checkpoint-every",
            "file",
            "--max-chunk-chars",
            "400",
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["ingest_id"] == "main-cli-ensemble"
    assert payload["counts"]["processed_source_count"] == 1
    assert (out_dir / "manifest.json").exists()
    claims = (out_dir / "claims.jsonl").read_text(encoding="utf-8")
    assert "A claim because the source states it." in claims


def test_main_ingest_ensemble_missing_source_exits_cleanly(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "ingest-ensemble",
            str(tmp_path / "missing"),
            "--out-dir",
            str(out_dir),
        ]
        with pytest.raises(SystemExit) as excinfo:
            didactopus_main.main()
    finally:
        sys.argv = original_argv

    assert "ingest-ensemble: Source root does not exist" in str(excinfo.value)
    assert not out_dir.exists()


def test_main_citations_from_ingest_command(tmp_path: Path, capsys) -> None:
    run = tmp_path / "ensemble"
    out_dir = tmp_path / "citation-out"
    run.mkdir()
    (run / "manifest.json").write_text(json.dumps({"ingest_id": "main-cli-citations"}), encoding="utf-8")
    (run / "sources.jsonl").write_text(
        json.dumps({"source_id": "src_cli", "path": "example.pdf"}) + "\n",
        encoding="utf-8",
    )
    (run / "fragments.jsonl").write_text(
        json.dumps(
            {
                "fragment_id": "frag_cli",
                "source_id": "src_cli",
                "source_path": "example.pdf",
                "section": "Main",
                "text": "References\nSmith, J. (2020). Example citation. Journal of Examples, 1, 1-2.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "citations-from-ingest",
            str(run),
            "--out-dir",
            str(out_dir),
            "--run-id",
            "main-cli-citation-pass",
            "--no-citegeist",
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["run_id"] == "main-cli-citation-pass"
    assert payload["counts"]["reference_candidate_count"] == 1
    assert payload["citegeist"]["status"] == "skipped"
    assert (out_dir / "citation_link_manifest.json").exists()


def test_main_source_spine_transfer_command(monkeypatch, tmp_path: Path, capsys) -> None:
    seen: dict[str, object] = {}

    def fake_run_experiment(**kwargs):
        seen.update(kwargs)
        return {
            "run_id": "source-spine-transfer-test",
            "artifacts": {"report": str(tmp_path / "groundedness_report.md")},
        }

    monkeypatch.setattr(didactopus_main, "run_source_spine_transfer_experiment", fake_run_experiment)
    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "source-spine-transfer",
            "--models",
            "model-a",
            "--conditions",
            "source_dump",
            "--out-dir",
            str(tmp_path),
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    output = capsys.readouterr().out
    assert "source-spine-transfer-test" in output
    assert seen["models"] == ["model-a"]
    assert seen["conditions"] == ["source_dump"]
    assert seen["out_dir"] == str(tmp_path)


def test_main_interoperability_registry_command(capsys) -> None:
    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "interoperability-registry",
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["validation"]["ok"] is True
    assert any(standard["standard_id"] == "qti" for standard in payload["standards"])


def test_main_pack_capsule_validate_command(tmp_path: Path, capsys) -> None:
    lesson = tmp_path / "lesson.md"
    lesson.write_text("# Lesson\n", encoding="utf-8")
    manifest = tmp_path / "didactopus-pack-capsule.json"
    manifest.write_text(
        json.dumps(
            {
                "capsule_id": "main-cli-capsule",
                "pack_name": "main-cli-pack",
                "title": "Main CLI Pack",
                "version": "0.1.0",
                "license": "CC-BY-4.0",
                "review_status": "reviewed",
                "content_files": [{"path": "lesson.md", "role": "source"}],
                "provenance_summary": "CLI validation fixture.",
                "accessibility_features": ["text_only"],
                "model_requirements": [{"role": "mentor"}],
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv
    try:
        sys.argv = [
            "didactopus.main",
            "pack-capsule-validate",
            str(manifest),
        ]
        didactopus_main.main()
    finally:
        sys.argv = original_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["summary"]["pack_name"] == "main-cli-pack"
