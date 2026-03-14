from __future__ import annotations
from pathlib import Path
import yaml

def load_concepts(path: str | Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return list(data.get("concepts", []) or [])
