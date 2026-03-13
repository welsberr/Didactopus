import argparse
import os
from pathlib import Path

from .adaptive_engine import LearnerProfile, build_adaptive_plan
from .artifact_registry import (
    check_pack_dependencies,
    detect_dependency_cycles,
    discover_domain_packs,
    topological_pack_order,
)
from .config import load_config
from .evidence_engine import EvidenceItem, ingest_evidence_bundle
from .learning_graph import build_merged_learning_graph
from .mentor import generate_socratic_prompt
from .model_provider import ModelProvider
from .practice import generate_practice_task
from .project_advisor import suggest_capstone


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus multi-dimensional mastery scaffold")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument(
        "--config",
        default=os.environ.get("DIDACTOPUS_CONFIG", "configs/config.example.yaml"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    provider = ModelProvider(config.model_provider)
    packs = discover_domain_packs(config.artifacts.local_pack_dirs)
    dependency_errors = check_pack_dependencies(packs)
    cycles = detect_dependency_cycles(packs)

    print("== Didactopus ==")
    print("Many arms, one goal — mastery.")
    print()

    if dependency_errors:
        print("== Dependency Errors ==")
        for err in dependency_errors:
            print(f"- {err}")
        print()

    if cycles:
        print("== Dependency Cycles ==")
        for cycle in cycles:
            print(f"- cycle: {' -> '.join(cycle)}")
        return

    print("== Pack Load Order ==")
    for name in topological_pack_order(packs):
        print(f"- {name}")
    print()

    merged = build_merged_learning_graph(packs)
    profile = LearnerProfile(
        learner_id="demo-learner",
        display_name="Demo Learner",
        goals=[args.goal],
        mastered_concepts=set(),
        hide_mastered=True,
    )

    evidence_items = [
        EvidenceItem(
            concept_key="foundations-statistics::descriptive-statistics",
            evidence_type="project",
            score=0.88,
            is_recent=True,
            rubric_dimensions={
                "correctness": 0.9,
                "explanation": 0.83,
                "transfer": 0.79,
                "project_execution": 0.88,
                "critique": 0.74,
            },
            notes="Strong integrated performance.",
        ),
        EvidenceItem(
            concept_key="bayes-extension::prior",
            evidence_type="problem",
            score=0.68,
            is_recent=True,
            rubric_dimensions={
                "correctness": 0.75,
                "explanation": 0.62,
                "transfer": 0.55,
                "critique": 0.58,
            },
            notes="Knows some basics, weak transfer and critique.",
        ),
    ]

    evidence_state = ingest_evidence_bundle(
        profile=profile,
        items=evidence_items,
        resurfacing_threshold=config.platform.resurfacing_threshold,
        confidence_threshold=config.platform.confidence_threshold,
        type_weights=config.platform.evidence_weights,
        recent_multiplier=config.platform.recent_evidence_multiplier,
        dimension_thresholds=config.platform.dimension_thresholds,
    )

    plan = build_adaptive_plan(merged, profile)

    print("== Multi-Dimensional Evidence Summary ==")
    for concept_key, summary in evidence_state.summary_by_concept.items():
        print(
            f"- {concept_key}: weighted_mean={summary.weighted_mean_score:.2f}, "
            f"confidence={summary.confidence:.2f}, mastered={summary.mastered}"
        )
        if summary.dimension_means:
            dims = ", ".join(f"{k}={v:.2f}" for k, v in sorted(summary.dimension_means.items()))
            print(f"  * dimensions: {dims}")
        if summary.weak_dimensions:
            print(f"  * weak dimensions: {', '.join(summary.weak_dimensions)}")
    print()

    print("== Mastered Concepts ==")
    if profile.mastered_concepts:
        for concept_key in sorted(profile.mastered_concepts):
            print(f"- {concept_key}")
    else:
        print("- none yet")
    print()

    print("== Next Best Concepts ==")
    for concept in plan.next_best_concepts:
        print(f"- {concept}")
    print()

    focus_concept = "bayes-extension::prior"
    weak_dims = evidence_state.summary_by_concept.get(focus_concept).weak_dimensions if focus_concept in evidence_state.summary_by_concept else []
    print(generate_socratic_prompt(provider, focus_concept, weak_dims))
    print(generate_practice_task(provider, focus_concept, weak_dims))
    print(suggest_capstone(provider, args.domain))
