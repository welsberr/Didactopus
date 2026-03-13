from didactopus.artifact_registry import discover_domain_packs
from didactopus.learning_graph import (
    build_merged_learning_graph,
    generate_learner_roadmap,
    namespaced_concept,
)


def _acyclic_results():
    return [
        r for r in discover_domain_packs(["domain-packs"])
        if r.manifest and r.manifest.name in {
            "foundations-statistics",
            "bayes-extension",
            "override-foundations",
        }
    ]


def test_namespaced_concept() -> None:
    assert namespaced_concept("pack", "concept") == "pack::concept"


def test_build_merged_learning_graph() -> None:
    merged = build_merged_learning_graph(_acyclic_results())
    assert "foundations-statistics::probability-basics" in merged.concept_data
    assert "bayes-extension::posterior" in merged.concept_data
    assert len(merged.stage_catalog) >= 3
    assert len(merged.project_catalog) >= 3


def test_override_updates_target_concept() -> None:
    merged = build_merged_learning_graph(_acyclic_results())
    data = merged.concept_data["foundations-statistics::descriptive-statistics"]
    assert data["title"] == "Descriptive Statistics (Overridden)"
    assert data["pack"] == "override-foundations"


def test_generate_learner_roadmap() -> None:
    merged = build_merged_learning_graph(_acyclic_results())
    roadmap = generate_learner_roadmap(merged)
    assert len(roadmap) >= 3
    assert all("concept_key" in item for item in roadmap)
