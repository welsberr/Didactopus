import sys
from pathlib import Path

from didactopus.groundrecall.cli import main as groundrecall_cli_main
from didactopus.groundrecall.export import export_canonical_bundle
from didactopus.groundrecall.ingest import run_groundrecall_import
from didactopus.groundrecall.inspect import inspect_store
from didactopus.groundrecall.models import ClaimRecord
from didactopus.groundrecall.query import query_concept
from didactopus.groundrecall.store import GroundRecallStore
from didactopus.groundrecall.promotion import promote_import_to_store


def _build_llmwiki_fixture(root: Path) -> Path:
    (root / "wiki").mkdir(parents=True)
    (root / "raw").mkdir()
    (root / "wiki" / "channel-capacity.md").write_text(
        "# Channel Capacity\n\n"
        "- Reliable rate upper bound for a noisy channel.\n\n"
        "See also [[Shannon Entropy]].\n",
        encoding="utf-8",
    )
    (root / "raw" / "notes.md").write_text(
        "Speculation: Capacity may depend on constraints.\n",
        encoding="utf-8",
    )
    return root


def test_groundrecall_namespace_reexports_core_functions() -> None:
    assert run_groundrecall_import.__module__ == "didactopus.groundrecall_import"
    assert query_concept.__module__ == "didactopus.groundrecall.query"
    assert export_canonical_bundle.__module__ == "didactopus.groundrecall.export"
    assert GroundRecallStore.__module__ == "didactopus.groundrecall_store"
    assert ClaimRecord.__module__ == "didactopus.groundrecall_models"


def test_groundrecall_inspect_summarizes_store(tmp_path: Path) -> None:
    source_root = _build_llmwiki_fixture(tmp_path / "llmwiki")
    import_result = run_groundrecall_import(source_root, out_root=tmp_path / "imports", mode="quick", import_id="fixture-import")
    store_dir = tmp_path / "store"
    promote_import_to_store(import_result.out_dir, store_dir)

    payload = inspect_store(store_dir, out_path=tmp_path / "inspect.json")

    assert (tmp_path / "inspect.json").exists()
    assert payload["claim_count"] >= 1
    assert payload["concept_count"] >= 1
    assert payload["snapshot_count"] >= 1


def test_groundrecall_cli_inspect_dispatches(tmp_path: Path, capsys) -> None:
    source_root = _build_llmwiki_fixture(tmp_path / "llmwiki")
    import_result = run_groundrecall_import(source_root, out_root=tmp_path / "imports", mode="quick", import_id="fixture-import")
    store_dir = tmp_path / "store"
    promote_import_to_store(import_result.out_dir, store_dir)

    original_argv = sys.argv
    try:
        sys.argv = ["didactopus.groundrecall.cli", "inspect", str(store_dir)]
        groundrecall_cli_main()
    finally:
        sys.argv = original_argv

    output = capsys.readouterr().out
    assert '"claim_count"' in output
    assert '"concept_count"' in output
