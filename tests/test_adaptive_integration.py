from didactopus.adaptive_engine import LearnerProfile, build_adaptive_plan
from didactopus.artifact_registry import discover_domain_packs
from didactopus.evidence_engine import EvidenceItem, ingest_evidence_bundle
from didactopus.learning_graph import build_merged_learning_graph


def test_evidence_drives_plan() -> None:
    merged = build_merged_learning_graph(discover_domain_packs(["domain-packs"]))
    profile = LearnerProfile(learner_id="u1")
    ingest_evidence_bundle(
        profile,
        [
            EvidenceItem("foundations-statistics::descriptive-statistics", "problem", 0.9),
            EvidenceItem("foundations-statistics::descriptive-statistics", "explanation", 0.85),
        ],
        mastery_threshold=0.8,
        resurfacing_threshold=0.55,
    )
    plan = build_adaptive_plan(merged, profile)
    assert "foundations-statistics::probability-basics" in plan.next_best_concepts
