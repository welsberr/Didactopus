from pathlib import Path

from didactopus.course_repo import bootstrap_course_repo, load_course_repo_manifest, resolve_course_repo
from didactopus.ocw_information_entropy_demo import bootstrap_ocw_course_repo_target, resolve_ocw_demo_paths


def test_load_and_resolve_course_repo_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "course").mkdir()
    (repo / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    (repo / "didactopus-course.yaml").write_text(
        "\n".join(
            [
                "course_id: sample-course",
                "display_name: Sample Course",
                "source_dir: course",
                "source_inventory: sources.yaml",
                "license_family: CC BY-NC-SA 4.0",
                "generated_pack_dir: generated/pack",
                "generated_run_dir: generated/run",
                "generated_skill_dir: generated/skill",
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_course_repo_manifest(repo)
    resolved = resolve_course_repo(repo)

    assert manifest.course_id == "sample-course"
    assert resolved.course_id == "sample-course"
    assert resolved.source_dir.endswith("/repo/course")
    assert resolved.generated_pack_dir.endswith("/repo/generated/pack")


def test_resolve_ocw_demo_paths_from_course_repo_manifest() -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = resolve_ocw_demo_paths(
        root,
        course_repo=root / "examples" / "ocw-information-entropy",
    )

    assert resolved["course_source"].endswith("/examples/ocw-information-entropy/course")
    assert resolved["source_inventory"].endswith("/examples/ocw-information-entropy/sources.yaml")
    assert resolved["pack_dir"].endswith("/domain-packs/mit-ocw-information-entropy")


def test_bootstrap_course_repo_copies_source_bundle(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "lesson.md").write_text("# T\n\n## M\n### L\nBody.", encoding="utf-8")
    inventory = tmp_path / "sources.yaml"
    inventory.write_text("sources: []\n", encoding="utf-8")

    resolved = bootstrap_course_repo(
        target_dir=tmp_path / "repo",
        course_id="sample-course",
        display_name="Sample Course",
        course_source=source_dir,
        source_inventory=inventory,
        license_family="CC BY-NC-SA 4.0",
    )

    assert Path(resolved.manifest_path).exists()
    assert Path(resolved.source_dir, "lesson.md").exists()
    assert Path(resolved.source_inventory).exists()


def test_bootstrap_ocw_course_repo_target_returns_generated_paths(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = bootstrap_ocw_course_repo_target(
        target_dir=tmp_path / "repo",
        root=root,
    )
    assert resolved["course_source"].endswith("/repo/course")
    assert resolved["pack_dir"].endswith("/repo/generated/pack")
