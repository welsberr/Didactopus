from pathlib import Path
from didactopus.pack_to_frontend import convert_pack

def test_convert_pack(tmp_path: Path):
    (tmp_path / "pack.yaml").write_text(
        "name: p1\ndisplay_name: Pack 1\ndescription: Demo pack\n", encoding="utf-8"
    )
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: c1\n    title: Concept 1\n    prerequisites: []\n", encoding="utf-8"
    )
    (tmp_path / "pack_compliance_manifest.json").write_text(
        '{"derived_from_sources":["s1"],"attribution_required":true,"share_alike_required":false,"noncommercial_only":false,"restrictive_flags":[]}',
        encoding="utf-8"
    )
    payload = convert_pack(tmp_path)
    assert payload["id"] == "p1"
    assert payload["concepts"][0]["id"] == "c1"
    assert payload["notebook"]["available"] is False


def test_convert_pack_surfaces_notebook_summary(tmp_path: Path):
    (tmp_path / "pack.yaml").write_text(
        "name: p2\ndisplay_name: Pack 2\ndescription: Demo pack with notebook\n", encoding="utf-8"
    )
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: c2\n    title: Concept 2\n    prerequisites: []\n", encoding="utf-8"
    )
    (tmp_path / "pack_compliance_manifest.json").write_text(
        '{"derived_from_sources":["s1"],"attribution_required":true,"share_alike_required":false,"noncommercial_only":false,"restrictive_flags":[]}',
        encoding="utf-8"
    )
    (tmp_path / "groundrecall_query_bundle.json").write_text(
        '{"bundle_kind":"groundrecall_query_bundle","concept":{"concept_id":"concept::thermo","title":"Thermodynamics and Entropy"},"relevant_claims":[{"claim_id":"c1"},{"claim_id":"c2"}],"source_role_summary":{"overview":1},"key_distinctions":[{"distinction_type":"non_implication"}]}',
        encoding="utf-8",
    )
    (tmp_path / "notebook_page.json").write_text(
        '{"concept":{"concept_id":"concept::thermo","title":"Thermodynamics and Entropy"},"summary":{"supporting_observation_count":3,"related_concept_count":2},"source_role_summary":{"overview":1},"distinctions":[{"distinction_type":"non_implication"}]}',
        encoding="utf-8",
    )

    payload = convert_pack(tmp_path)
    assert payload["notebook"]["available"] is True
    assert payload["notebook"]["conceptTitle"] == "Thermodynamics and Entropy"
    assert payload["notebook"]["claimCount"] == 2
    assert payload["notebook"]["sourceRoleSummary"]["overview"] == 1
    assert payload["notebook"]["distinctionCount"] == 1
    assert payload["notebook"]["supportingObservationCount"] == 3
