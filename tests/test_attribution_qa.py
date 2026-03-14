from pathlib import Path
from didactopus.attribution_qa import attribution_qa

def test_attribution_qa_detects_missing_fields(tmp_path: Path) -> None:
    p = tmp_path / "sources.yaml"
    p.write_text(
        "sources:\n"
        "  - source_id: s1\n"
        "    title: Example\n"
        "    url: ''\n"
        "    license_id: CC BY-NC-SA 4.0\n"
        "    license_url: ''\n"
        "    attribution_text: ''\n",
        encoding="utf-8",
    )
    result = attribution_qa(p)
    assert len(result["warnings"]) >= 3
