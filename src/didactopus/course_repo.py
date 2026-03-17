from __future__ import annotations

from pathlib import Path
import shutil

import yaml
from pydantic import BaseModel


class CourseRepoManifest(BaseModel):
    course_id: str
    display_name: str
    source_dir: str
    source_inventory: str
    license_family: str = ""
    generated_pack_dir: str | None = None
    generated_run_dir: str | None = None
    generated_skill_dir: str | None = None


class ResolvedCourseRepo(BaseModel):
    repo_root: str
    manifest_path: str
    course_id: str
    display_name: str
    license_family: str = ""
    source_dir: str
    source_inventory: str
    generated_pack_dir: str | None = None
    generated_run_dir: str | None = None
    generated_skill_dir: str | None = None


def course_repo_manifest_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_dir():
        return candidate / "didactopus-course.yaml"
    return candidate


def load_course_repo_manifest(path: str | Path) -> CourseRepoManifest:
    manifest_path = course_repo_manifest_path(path)
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    return CourseRepoManifest.model_validate(data)


def resolve_course_repo(path: str | Path) -> ResolvedCourseRepo:
    manifest_path = course_repo_manifest_path(path).resolve()
    repo_root = manifest_path.parent
    manifest = load_course_repo_manifest(manifest_path)

    def _resolve(relpath: str | None) -> str | None:
        if relpath is None:
            return None
        return str((repo_root / relpath).resolve())

    return ResolvedCourseRepo(
        repo_root=str(repo_root),
        manifest_path=str(manifest_path),
        course_id=manifest.course_id,
        display_name=manifest.display_name,
        license_family=manifest.license_family,
        source_dir=_resolve(manifest.source_dir) or "",
        source_inventory=_resolve(manifest.source_inventory) or "",
        generated_pack_dir=_resolve(manifest.generated_pack_dir),
        generated_run_dir=_resolve(manifest.generated_run_dir),
        generated_skill_dir=_resolve(manifest.generated_skill_dir),
    )


def initialize_course_repo(
    target_dir: str | Path,
    course_id: str,
    display_name: str,
    license_family: str = "",
    source_dir_name: str = "course",
    source_inventory_name: str = "sources.yaml",
    generated_pack_dir: str = "generated/pack",
    generated_run_dir: str = "generated/run",
    generated_skill_dir: str = "generated/skill",
) -> ResolvedCourseRepo:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    manifest_path = target / "didactopus-course.yaml"
    if not manifest_path.exists():
        payload = {
            "course_id": course_id,
            "display_name": display_name,
            "source_dir": source_dir_name,
            "source_inventory": source_inventory_name,
            "license_family": license_family,
            "generated_pack_dir": generated_pack_dir,
            "generated_run_dir": generated_run_dir,
            "generated_skill_dir": generated_skill_dir,
        }
        manifest_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    (target / source_dir_name).mkdir(parents=True, exist_ok=True)
    inventory_path = target / source_inventory_name
    if not inventory_path.exists():
        inventory_path.write_text("sources: []\n", encoding="utf-8")
    return resolve_course_repo(target)


def populate_course_repo_sources(
    target_dir: str | Path,
    course_source: str | Path,
    source_inventory: str | Path,
    source_dir_name: str = "course",
    source_inventory_name: str = "sources.yaml",
    overwrite: bool = True,
) -> ResolvedCourseRepo:
    target = Path(target_dir)
    source_path = Path(course_source)
    inventory_path = Path(source_inventory)
    target_source = target / source_dir_name
    target_inventory = target / source_inventory_name

    if overwrite and target_source.exists():
        shutil.rmtree(target_source)
    target_source.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        for child in sorted(source_path.iterdir()):
            if child.is_dir():
                shutil.copytree(child, target_source / child.name, dirs_exist_ok=True)
            else:
                shutil.copy2(child, target_source / child.name)
    else:
        shutil.copy2(source_path, target_source / source_path.name)

    shutil.copy2(inventory_path, target_inventory)
    return resolve_course_repo(target)


def bootstrap_course_repo(
    target_dir: str | Path,
    course_id: str,
    display_name: str,
    course_source: str | Path,
    source_inventory: str | Path,
    license_family: str = "",
    overwrite: bool = True,
) -> ResolvedCourseRepo:
    resolved = initialize_course_repo(
        target_dir=target_dir,
        course_id=course_id,
        display_name=display_name,
        license_family=license_family,
    )
    return populate_course_repo_sources(
        target_dir=resolved.repo_root,
        course_source=course_source,
        source_inventory=source_inventory,
        overwrite=overwrite,
    )
