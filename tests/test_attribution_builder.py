from pathlib import Path
from didactopus.attribution_builder import build_artifacts

def test_build_artifacts(tmp_path: Path) -> None:
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        "sources:\n"
        "  - source_id: s1\n"
        "    title: Example\n"
        "    url: https://example.org\n"
        "    publisher: Example Publisher\n"
        "    creator: Example Creator\n"
        "    license_id: CC BY-NC-SA 4.0\n"
        "    license_url: https://creativecommons.org/licenses/by-nc-sa/4.0/\n"
        "    attribution_text: Example attribution\n",
        encoding="utf-8",
    )
    attr = tmp_path / "ATTRIBUTION.md"
    manifest = tmp_path / "provenance_manifest.json"
    build_artifacts(sources, attr, manifest)
    assert attr.exists()
    assert manifest.exists()
