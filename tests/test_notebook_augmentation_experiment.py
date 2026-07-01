from pathlib import Path
import json

from didactopus.notebook_augmentation_experiment import compare_notebook_packs, write_notebook_comparison_report


def _write_pack(
    root: Path,
    *,
    claim_count: int,
    source_role_summary: dict,
    distinction_count: int,
    supporting_observation_count: int,
    related_concept_count: int,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pack.yaml").write_text(
        "name: demo-pack\ndisplay_name: Demo Pack\ndescription: Demo\n",
        encoding="utf-8",
    )
    (root / "concepts.yaml").write_text(
        "concepts:\n  - id: thermo\n    title: Thermodynamics and Entropy\n    prerequisites: []\n",
        encoding="utf-8",
    )
    (root / "groundrecall_query_bundle.json").write_text(
        json.dumps(
            {
                "bundle_kind": "groundrecall_query_bundle",
                "concept": {"concept_id": "concept::thermo", "title": "Thermodynamics and Entropy"},
                "relevant_claims": [{"claim_id": f"c{i+1}"} for i in range(claim_count)],
                "source_role_summary": source_role_summary,
                "key_distinctions": [{"distinction_type": "contrast"} for _ in range(distinction_count)],
            }
        ),
        encoding="utf-8",
    )
    (root / "notebook_page.json").write_text(
        json.dumps(
            {
                "concept": {"concept_id": "concept::thermo", "title": "Thermodynamics and Entropy"},
                "summary": {
                    "supporting_observation_count": supporting_observation_count,
                    "related_concept_count": related_concept_count,
                },
                "source_role_summary": source_role_summary,
                "distinctions": [{"distinction_type": "contrast"} for _ in range(distinction_count)],
            }
        ),
        encoding="utf-8",
    )


def test_compare_notebook_packs_reports_deltas(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    augmented = tmp_path / "augmented"
    _write_pack(
        baseline,
        claim_count=3,
        source_role_summary={"overview": 1},
        distinction_count=0,
        supporting_observation_count=3,
        related_concept_count=2,
    )
    _write_pack(
        augmented,
        claim_count=7,
        source_role_summary={"overview": 3, "nuance": 4},
        distinction_count=5,
        supporting_observation_count=7,
        related_concept_count=2,
    )

    comparison = compare_notebook_packs(baseline, augmented)
    assert comparison["delta"]["claimCount"] == 4
    assert comparison["delta"]["distinctionCount"] == 5
    assert comparison["delta"]["sourceRoleKeys"] == ["nuance"]


def test_write_notebook_comparison_report_emits_files(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    augmented = tmp_path / "augmented"
    outdir = tmp_path / "report"
    _write_pack(
        baseline,
        claim_count=1,
        source_role_summary={"overview": 1},
        distinction_count=0,
        supporting_observation_count=1,
        related_concept_count=1,
    )
    _write_pack(
        augmented,
        claim_count=2,
        source_role_summary={"overview": 1, "nuance": 1},
        distinction_count=1,
        supporting_observation_count=2,
        related_concept_count=1,
    )

    write_notebook_comparison_report(baseline, augmented, outdir, title="Demo")
    assert (outdir / "comparison.json").exists()
    assert (outdir / "comparison.md").exists()
    assert (outdir / "frontend_pack_with_notebook.json").exists()
