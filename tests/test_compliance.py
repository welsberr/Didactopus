from pathlib import Path
from didactopus.course_ingestion_compliance import load_sources, build_pack_compliance_manifest, compliance_qa

def test_build_manifest_and_qa(tmp_path: Path):
    p = tmp_path / "sources.yaml"
    p.write_text(
        "sources:\n"
        "  - source_id: s1\n"
        "    title: Example\n"
        "    url: https://example.org\n"
        "    license_id: CC BY-NC-SA 4.0\n"
        "    license_url: https://creativecommons.org/licenses/by-nc-sa/4.0/\n"
        "    attribution_text: Example attribution\n",
        encoding="utf-8",
    )
    inv = load_sources(p)
    manifest = build_pack_compliance_manifest("p1", "Pack 1", inv)
    qa = compliance_qa(inv, manifest)
    assert manifest.share_alike_required is True
    assert manifest.noncommercial_only is True
    assert qa["summary"]["source_count"] == 1
