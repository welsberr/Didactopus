import argparse
import os
from pathlib import Path

from .adaptive_engine import LearnerProfile, build_adaptive_plan
from .artifact_registry import check_pack_dependencies, detect_dependency_cycles, discover_domain_packs, topological_pack_order
from .config import load_config
from .evidence_engine import EvidenceItem, ingest_evidence_bundle
from .evaluation import score_simple_rubric
from .learning_graph import build_merged_learning_graph
from .mentor import generate_socratic_prompt
from .model_provider import ModelProvider
from .practice import generate_practice_task
from .project_advisor import suggest_capstone


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus evidence-driven mastery scaffold")
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

    demo_score = score_simple_rubric(0.9, 0.85, 0.8, 0.75)
    evidence_items = [
        EvidenceItem(
            concept_key="foundations-statistics::descriptive-statistics",
            evidence_type="explanation",
            score=demo_score.mean(),
            notes="Strong introductory explanation.",
        ),
        EvidenceItem(
            concept_key="foundations-statistics::descriptive-statistics",
            evidence_type="problem",
            score=0.88,
            notes="Solved summary statistics problem correctly.",
        ),
        EvidenceItem(
            concept_key="bayes-extension::prior",
            evidence_type="explanation",
            score=0.62,
            notes="Partial understanding of priors.",
        ),
    ]
    evidence_state = ingest_evidence_bundle(
        profile=profile,
        items=evidence_items,
        mastery_threshold=config.platform.mastery_threshold,
        resurfacing_threshold=config.platform.resurfacing_threshold,
    )

    plan = build_adaptive_plan(merged, profile)

    print("== Evidence Summary ==")
    for concept_key, summary in evidence_state.summary_by_concept.items():
        print(f"- {concept_key}: count={summary.count}, mean={summary.mean_score:.2f}")
    print()
    print("== Mastered Concepts After Evidence ==")
    for concept_key in sorted(profile.mastered_concepts):
        print(f"- {concept_key}")
    print()
    print("== Resurfaced Concepts ==")
    if evidence_state.resurfaced_concepts:
        for concept_key in sorted(evidence_state.resurfaced_concepts):
            print(f"- {concept_key}")
    else:
        print("- none")
    print()
    print("== Adaptive Plan Summary ==")
    print(f"- roadmap items visible: {len(plan.learner_roadmap)}")
    print(f"- next-best concepts: {len(plan.next_best_concepts)}")
    print(f"- eligible projects: {len(plan.eligible_projects)}")
    print()
    print("== Next Best Concepts ==")
    for concept in plan.next_best_concepts:
        print(f"- {concept}")
    print()
    print("== Eligible Projects ==")
    if plan.eligible_projects:
        for project in plan.eligible_projects:
            print(f"- {project['id']}: {project['title']}")
    else:
        print("- none yet")
    print()

    focus_concept = plan.next_best_concepts[0] if plan.next_best_concepts else args.domain
    print(generate_socratic_prompt(provider, focus_concept))
    print(generate_practice_task(provider, focus_concept))
    print(suggest_capstone(provider, args.domain))
