from __future__ import annotations

from pathlib import Path
import sys

from .doclift_bundle_demo import run_doclift_bundle_demo


def run_doclift_bundle_with_groundrecall(
    *,
    groundrecall_store_dir: str | Path,
    groundrecall_concept_ref: str,
    bundle_dir: str | Path,
    course_title: str,
    pack_dir: str | Path,
    author: str = "doclift bundle import",
    license_name: str = "See source bundle metadata",
) -> dict:
    export_groundrecall_query_bundle = _load_groundrecall_export()
    pack_dir = Path(pack_dir)
    export_dir = pack_dir / "_groundrecall"
    exported = export_groundrecall_query_bundle(
        groundrecall_store_dir,
        groundrecall_concept_ref,
        export_dir,
    )
    summary = run_doclift_bundle_demo(
        bundle_dir=bundle_dir,
        course_title=course_title,
        pack_dir=pack_dir,
        author=author,
        license_name=license_name,
        groundrecall_query_bundle_path=exported["bundle_path"],
    )
    summary["groundrecall_concept_ref"] = groundrecall_concept_ref
    summary["groundrecall_query_bundle_path"] = exported["bundle_path"]
    return summary


def _load_groundrecall_export():
    groundrecall_src = Path("/home/netuser/bin/GroundRecall/src")
    if groundrecall_src.exists():
        sys.path.insert(0, str(groundrecall_src))
    from groundrecall.export import export_groundrecall_query_bundle  # type: ignore

    return export_groundrecall_query_bundle
