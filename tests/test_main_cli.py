from __future__ import annotations

from pathlib import Path

import didactopus.main as main_module


def test_main_doclift_bundle_subcommand(monkeypatch, capsys, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_run_doclift_bundle_demo(bundle_dir, course_title, pack_dir, author, license_name):
        captured.update(
            {
                "bundle_dir": str(bundle_dir),
                "course_title": course_title,
                "pack_dir": str(pack_dir),
                "author": author,
                "license_name": license_name,
            }
        )
        return {"pack_dir": str(pack_dir), "course_title": course_title}

    monkeypatch.setattr(main_module, "run_doclift_bundle_demo", _fake_run_doclift_bundle_demo)
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        [
            "didactopus",
            "doclift-bundle",
            str(tmp_path / "bundle"),
            str(tmp_path / "pack"),
            "--course-title",
            "Example Course",
        ],
    )

    main_module.main()
    out = capsys.readouterr().out

    assert captured["course_title"] == "Example Course"
    assert "Example Course" in out


def test_main_doclift_bundle_groundrecall_subcommand(monkeypatch, capsys, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_run_doclift_bundle_with_groundrecall(**kwargs):
        captured.update({key: str(value) for key, value in kwargs.items()})
        return {"pack_dir": str(kwargs["pack_dir"]), "course_title": kwargs["course_title"]}

    monkeypatch.setattr(main_module, "run_doclift_bundle_with_groundrecall", _fake_run_doclift_bundle_with_groundrecall)
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        [
            "didactopus",
            "doclift-bundle-groundrecall",
            str(tmp_path / "store"),
            "channel-capacity",
            str(tmp_path / "bundle"),
            str(tmp_path / "pack"),
            "--course-title",
            "Example Course",
        ],
    )

    main_module.main()
    out = capsys.readouterr().out

    assert captured["groundrecall_concept_ref"] == "channel-capacity"
    assert captured["course_title"] == "Example Course"
    assert "Example Course" in out


def test_main_legacy_review_mode_uses_review_parser(monkeypatch, tmp_path: Path) -> None:
    called: dict = {}

    def _fake_run_review_workflow(args):
        called["draft_pack"] = args.draft_pack
        called["output_dir"] = args.output_dir

    monkeypatch.setattr(main_module, "run_review_workflow", _fake_run_review_workflow)
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        [
            "didactopus",
            "--draft-pack",
            str(tmp_path / "draft"),
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )

    main_module.main()

    assert called["draft_pack"] == str(tmp_path / "draft")
    assert called["output_dir"] == str(tmp_path / "out")


def test_main_notebook_page_subcommand(monkeypatch, capsys, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_export_notebook_page_from_groundrecall_bundle(bundle_path, out_path):
        captured["bundle_path"] = str(bundle_path)
        captured["out_path"] = str(out_path)
        return {"page_path": str(out_path)}

    monkeypatch.setattr(main_module, "export_notebook_page_from_groundrecall_bundle", _fake_export_notebook_page_from_groundrecall_bundle)
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        [
            "didactopus",
            "notebook-page",
            str(tmp_path / "groundrecall_query_bundle.json"),
            str(tmp_path / "notebook_page.json"),
        ],
    )

    main_module.main()
    out = capsys.readouterr().out

    assert captured["bundle_path"].endswith("groundrecall_query_bundle.json")
    assert captured["out_path"].endswith("notebook_page.json")
    assert "page_path" in out


def test_main_notebook_page_groundrecall_subcommand(monkeypatch, capsys, tmp_path: Path) -> None:
    captured: dict = {}

    def _fake_export_notebook_page_from_groundrecall_store(store_dir, concept_ref, out_dir):
        captured["store_dir"] = str(store_dir)
        captured["concept_ref"] = concept_ref
        captured["out_dir"] = str(out_dir)
        return {"page_path": str(Path(out_dir) / "notebook_page.json")}

    monkeypatch.setattr(main_module, "export_notebook_page_from_groundrecall_store", _fake_export_notebook_page_from_groundrecall_store)
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        [
            "didactopus",
            "notebook-page-groundrecall",
            str(tmp_path / "store"),
            "natural-selection",
            str(tmp_path / "out"),
        ],
    )

    main_module.main()
    out = capsys.readouterr().out

    assert captured["concept_ref"] == "natural-selection"
    assert captured["out_dir"].endswith("out")
    assert "page_path" in out
