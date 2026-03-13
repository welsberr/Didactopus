from dataclasses import dataclass, field, asdict
from pathlib import Path
import json


@dataclass
class CapabilityProfile:
    learner_id: str
    display_name: str
    domain: str
    mastered_concepts: list[str] = field(default_factory=list)
    weak_dimensions_by_concept: dict[str, list[str]] = field(default_factory=dict)
    evaluator_summary_by_concept: dict[str, dict] = field(default_factory=dict)
    artifacts: list[dict] = field(default_factory=list)


def build_capability_profile(state, domain: str) -> CapabilityProfile:
    weak = {}
    summaries = {}
    for concept, summary in state.evidence_state.summary_by_concept.items():
        weak[concept] = list(summary.weak_dimensions)
        summaries[concept] = dict(summary.aggregated)
    return CapabilityProfile(
        learner_id=state.learner_id,
        display_name=state.display_name,
        domain=domain,
        mastered_concepts=sorted(state.mastered_concepts),
        weak_dimensions_by_concept=weak,
        evaluator_summary_by_concept=summaries,
        artifacts=list(state.artifacts),
    )


def export_capability_profile_json(profile: CapabilityProfile, path: str) -> None:
    Path(path).write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")


def export_capability_report_markdown(profile: CapabilityProfile, path: str) -> None:
    lines = [
        f"# Capability Profile: {profile.display_name}",
        "",
        f"- Learner ID: `{profile.learner_id}`",
        f"- Domain: `{profile.domain}`",
        "",
        "## Mastered Concepts",
    ]
    if profile.mastered_concepts:
        lines.extend([f"- {c}" for c in profile.mastered_concepts])
    else:
        lines.append("- none")
    lines.extend(["", "## Concept Summaries"])
    if profile.evaluator_summary_by_concept:
        for concept, dims in sorted(profile.evaluator_summary_by_concept.items()):
            lines.append(f"### {concept}")
            if dims:
                for dim, score in sorted(dims.items()):
                    lines.append(f"- {dim}: {score:.2f}")
            weak = profile.weak_dimensions_by_concept.get(concept, [])
            lines.append(f"- weak dimensions: {', '.join(weak) if weak else 'none'}")
            lines.append("")
    else:
        lines.append("- none")
    lines.extend(["## Artifacts"])
    if profile.artifacts:
        for art in profile.artifacts:
            lines.append(f"- {art['artifact_name']} ({art['artifact_type']}) for {art['concept']}")
    else:
        lines.append("- none")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def export_artifact_manifest(profile: CapabilityProfile, path: str) -> None:
    manifest = {
        "learner_id": profile.learner_id,
        "domain": profile.domain,
        "artifacts": profile.artifacts,
    }
    Path(path).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
