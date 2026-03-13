from pathlib import Path
from didactopus.artifact_registry import discover_domain_packs
from didactopus.config import load_config
from didactopus.graph_builder import build_concept_graph


def test_exports(tmp_path: Path) -> None:
    config = load_config("configs/config.example.yaml")
    results = discover_domain_packs(["domain-packs"])
    graph = build_concept_graph(results, config.platform.default_dimension_thresholds)

    dot_path = tmp_path / "graph.dot"
    json_path = tmp_path / "graph.json"

    graph.export_graphviz(str(dot_path))
    graph.export_cytoscape_json(str(json_path))

    assert dot_path.exists()
    assert json_path.exists()
