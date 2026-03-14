from pathlib import Path
from didactopus.pack_to_frontend import convert_pack

def test_convert_pack(tmp_path: Path):
    (tmp_path / "pack.yaml").write_text("name: p1\ndisplay_name: Pack 1\ndescription: Demo pack\n", encoding="utf-8")
    (tmp_path / "concepts.yaml").write_text("concepts:\n  - id: c1\n    title: Concept 1\n    prerequisites: []\n", encoding="utf-8")
    (tmp_path / "pack_compliance_manifest.json").write_text('{"derived_from_sources":["s1"],"attribution_required":true,"share_alike_required":false,"noncommercial_only":false,"restrictive_flags":[]}', encoding="utf-8")
    payload = convert_pack(tmp_path)
    assert payload["id"] == "p1"
    assert payload["concepts"][0]["id"] == "c1"
