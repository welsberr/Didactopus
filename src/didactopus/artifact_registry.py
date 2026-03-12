from pathlib import Path
from pydantic import BaseModel
import yaml


class ArtifactManifest(BaseModel):
    name: str
    display_name: str
    version: str
    schema_version: str
    description: str = ""
    author: str = ""
    license: str = "unspecified"


def discover_domain_packs(base_dirs: list[str | Path]) -> list[tuple[Path, ArtifactManifest]]:
    packs: list[tuple[Path, ArtifactManifest]] = []
    for base_dir in base_dirs:
        base_path = Path(base_dir)
        if not base_path.exists():
            continue
        for pack_dir in sorted(p for p in base_path.iterdir() if p.is_dir()):
            manifest_path = pack_dir / "pack.yaml"
            if not manifest_path.exists():
                continue
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            packs.append((pack_dir, ArtifactManifest.model_validate(data)))
    return packs
