from pathlib import Path

from didactopus.ocw_information_entropy_demo import run_ocw_information_entropy_demo


def test_ocw_information_entropy_demo_generates_pack_and_skill(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    summary = run_ocw_information_entropy_demo(
        course_source=root / "examples" / "ocw-information-entropy" / "6-050j-information-and-entropy.md",
        source_inventory=root / "examples" / "ocw-information-entropy" / "sources.yaml",
        pack_dir=tmp_path / "pack",
        run_dir=tmp_path / "run",
        skill_dir=tmp_path / "skill",
    )

    assert (tmp_path / "pack" / "pack.yaml").exists()
    assert (tmp_path / "pack" / "pack_compliance_manifest.json").exists()
    assert (tmp_path / "run" / "capability_profile.json").exists()
    assert (tmp_path / "skill" / "SKILL.md").exists()
    assert summary["target_concept"].endswith("thermodynamics-and-entropy")
    assert summary["mastered_concepts"]
