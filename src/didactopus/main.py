import argparse
from pathlib import Path

from .agentic_loop import run_demo_agentic_loop
from .mastery_ledger import (
    build_capability_profile,
    export_capability_profile_json,
    export_capability_report_markdown,
    export_artifact_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Didactopus mastery ledger demo")
    parser.add_argument("--domain", default="Bayesian inference")
    parser.add_argument("--outdir", default="exports")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    concepts = [
        "foundations-statistics::descriptive-statistics",
        "foundations-statistics::probability-basics",
        "bayes-extension::prior",
        "bayes-extension::posterior",
        "applied-inference::model-checking",
    ]
    state = run_demo_agentic_loop(concepts)
    profile = build_capability_profile(state, args.domain)

    json_path = outdir / "capability_profile.json"
    md_path = outdir / "capability_report.md"
    manifest_path = outdir / "artifact_manifest.json"

    export_capability_profile_json(profile, str(json_path))
    export_capability_report_markdown(profile, str(md_path))
    export_artifact_manifest(profile, str(manifest_path))

    print("== Didactopus Mastery Ledger Demo ==")
    print(f"Domain: {args.domain}")
    print(f"Mastered concepts: {len(profile.mastered_concepts)}")
    print(f"Artifacts: {len(profile.artifacts)}")
    print(f"Capability profile JSON: {json_path}")
    print(f"Capability report Markdown: {md_path}")
    print(f"Artifact manifest JSON: {manifest_path}")
