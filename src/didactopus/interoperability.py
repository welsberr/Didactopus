from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator


AdapterStatus = Literal["implemented", "planned", "candidate", "avoid_primary", "legacy"]
MappingStatus = Literal["canonical", "lossy_export", "draft_import", "future_candidate"]
Direction = Literal["import", "export", "bidirectional", "metadata_only"]
AccessDefault = Literal["enabled", "enabled_local_only", "disabled", "metadata_only"]
StackComponent = Literal["Didactopus", "GroundRecall", "doclift", "CiteGeist", "SciSiteForge", "GenieHive", "forge_guardrails"]


class StandardRecord(BaseModel):
    standard_id: str
    name: str
    steward: str
    category: str
    purpose: str
    adapter_status: AdapterStatus
    owning_components: list[StackComponent]
    access_constrained_default: AccessDefault
    adoption_notes: str


class CrosswalkRecord(BaseModel):
    internal_object: str
    external_standard_id: str
    direction: Direction
    mapping_status: MappingStatus
    owning_component: StackComponent
    privacy_default: AccessDefault
    notes: str


class InteroperabilityRegistry(BaseModel):
    registry_schema_version: str = "didactopus-interoperability-registry-v0"
    standards: list[StandardRecord]
    crosswalks: list[CrosswalkRecord]
    default_policy: dict[str, str]

    def standards_by_id(self) -> dict[str, StandardRecord]:
        return {standard.standard_id: standard for standard in self.standards}

    def validate_crosswalk_targets(self) -> list[str]:
        known = set(self.standards_by_id())
        return [
            f"Crosswalk references unknown standard: {crosswalk.external_standard_id}"
            for crosswalk in self.crosswalks
            if crosswalk.external_standard_id not in known
        ]


class CapsuleFile(BaseModel):
    path: str
    role: str
    required: bool = True
    sha256: str | None = None
    media_type: str | None = None


class ModelRequirement(BaseModel):
    role: str
    minimum_context_tokens: int | None = None
    minimum_vram_gb: float | None = None
    tested_routes: list[str] = Field(default_factory=list)
    adequacy_report: str | None = None


class CapsuleAdapter(BaseModel):
    standard_id: str
    direction: Direction
    mapping_status: MappingStatus
    artifact_path: str | None = None
    notes: str = ""


class PackCapsuleManifest(BaseModel):
    schema_version: str = "didactopus-pack-capsule-v0"
    capsule_id: str
    pack_name: str
    title: str
    version: str
    language: str = "und"
    license: str
    review_status: Literal["draft", "reviewed", "trusted", "promoted"]
    content_files: list[CapsuleFile]
    provenance_summary: str
    accessibility_features: list[str] = Field(default_factory=list)
    model_requirements: list[ModelRequirement] = Field(default_factory=list)
    external_adapters: list[CapsuleAdapter] = Field(default_factory=list)
    privacy_profile: Literal["local_only", "shared_local", "institutional_export"] = "local_only"
    telemetry_enabled: bool = False
    remote_routes_allowed: bool = False

    @model_validator(mode="after")
    def _privacy_defaults_are_conservative(self) -> "PackCapsuleManifest":
        if self.privacy_profile == "local_only" and self.telemetry_enabled:
            raise ValueError("local_only pack capsules must not enable telemetry")
        if self.privacy_profile == "local_only" and self.remote_routes_allowed:
            raise ValueError("local_only pack capsules must not allow remote routes by default")
        return self


def build_interoperability_registry() -> InteroperabilityRegistry:
    def crosswalk(
        internal_object: str,
        external_standard_id: str,
        direction: Direction,
        mapping_status: MappingStatus,
        owning_component: StackComponent,
        privacy_default: AccessDefault,
        notes: str,
    ) -> CrosswalkRecord:
        return CrosswalkRecord(
            internal_object=internal_object,
            external_standard_id=external_standard_id,
            direction=direction,
            mapping_status=mapping_status,
            owning_component=owning_component,
            privacy_default=privacy_default,
            notes=notes,
        )

    standards = [
        StandardRecord(
            standard_id="common_cartridge",
            name="1EdTech Common Cartridge",
            steward="1EdTech",
            category="course_package",
            purpose="Course and learning-resource package exchange with LMSs.",
            adapter_status="planned",
            owning_components=["Didactopus", "doclift"],
            access_constrained_default="metadata_only",
            adoption_notes="Boundary adapter only; Didactopus pack capsules remain canonical.",
        ),
        StandardRecord(
            standard_id="qti",
            name="1EdTech Question and Test Interoperability",
            steward="1EdTech",
            category="assessment",
            purpose="Assessment item and test interchange.",
            adapter_status="planned",
            owning_components=["Didactopus", "doclift"],
            access_constrained_default="enabled_local_only",
            adoption_notes="Export reviewed items; import into draft review queues.",
        ),
        StandardRecord(
            standard_id="h5p",
            name="H5P",
            steward="H5P community",
            category="interactive_content",
            purpose="Reusable interactive HTML5 learning activities.",
            adapter_status="candidate",
            owning_components=["Didactopus", "doclift"],
            access_constrained_default="metadata_only",
            adoption_notes="Index and launch assets first; export only simple stable activities later.",
        ),
        StandardRecord(
            standard_id="xapi",
            name="Experience API",
            steward="ADL",
            category="learner_events",
            purpose="Learner activity statement interchange.",
            adapter_status="planned",
            owning_components=["Didactopus", "forge_guardrails"],
            access_constrained_default="disabled",
            adoption_notes="Optional export from local events; disabled by default in private profiles.",
        ),
        StandardRecord(
            standard_id="caliper",
            name="1EdTech Caliper Analytics",
            steward="1EdTech",
            category="analytics",
            purpose="Institutional learning analytics event interchange.",
            adapter_status="candidate",
            owning_components=["Didactopus", "forge_guardrails"],
            access_constrained_default="disabled",
            adoption_notes="Institutional integration only; not part of offline baseline.",
        ),
        StandardRecord(
            standard_id="case",
            name="1EdTech CASE",
            steward="1EdTech",
            category="competency",
            purpose="Academic standards and competency identifier exchange.",
            adapter_status="planned",
            owning_components=["Didactopus", "GroundRecall"],
            access_constrained_default="metadata_only",
            adoption_notes="Use reviewed mappings; never force one-to-one concept aliases.",
        ),
        StandardRecord(
            standard_id="skos_jsonld",
            name="SKOS / JSON-LD",
            steward="W3C",
            category="concept_scheme",
            purpose="Concept scheme and semantic relation exchange.",
            adapter_status="planned",
            owning_components=["GroundRecall", "Didactopus"],
            access_constrained_default="metadata_only",
            adoption_notes="Useful for cross-pack concept exports where relation loss is acceptable.",
        ),
        StandardRecord(
            standard_id="schema_org_learning_resource",
            name="Schema.org LearningResource/Course",
            steward="Schema.org",
            category="public_metadata",
            purpose="Machine-readable metadata for public educational pages.",
            adapter_status="planned",
            owning_components=["SciSiteForge", "Didactopus"],
            access_constrained_default="metadata_only",
            adoption_notes="Public-safe reviewed pages only.",
        ),
        StandardRecord(
            standard_id="w3c_prov",
            name="W3C PROV",
            steward="W3C",
            category="provenance",
            purpose="Entity/activity/agent provenance exchange.",
            adapter_status="planned",
            owning_components=["GroundRecall", "doclift", "SciSiteForge"],
            access_constrained_default="metadata_only",
            adoption_notes="GroundRecall owns canonical provenance; public exports must respect policy.",
        ),
        StandardRecord(
            standard_id="csl_json",
            name="CSL-JSON",
            steward="Citation Style Language project",
            category="citation",
            purpose="Bibliographic citation data interchange.",
            adapter_status="planned",
            owning_components=["CiteGeist", "GroundRecall"],
            access_constrained_default="metadata_only",
            adoption_notes="Use with BibTeX/BibLaTeX, DOI, ORCID, and source anchors.",
        ),
        StandardRecord(
            standard_id="wcag_22",
            name="Web Content Accessibility Guidelines 2.2",
            steward="W3C",
            category="accessibility",
            purpose="Accessibility baseline for learner-facing web surfaces.",
            adapter_status="planned",
            owning_components=["Didactopus", "SciSiteForge"],
            access_constrained_default="enabled",
            adoption_notes="Target WCAG 2.2 AA for learner surfaces.",
        ),
        StandardRecord(
            standard_id="epub3",
            name="EPUB 3",
            steward="W3C Publishing Community Group",
            category="offline_reading",
            purpose="Portable offline learner guides and study packets.",
            adapter_status="planned",
            owning_components=["Didactopus", "doclift"],
            access_constrained_default="enabled_local_only",
            adoption_notes="Generate accessible study packets; ingest EPUB source material later.",
        ),
        StandardRecord(
            standard_id="openzim_zim",
            name="openZIM / ZIM",
            steward="openZIM/Kiwix community",
            category="offline_content",
            purpose="Offline web content archive and serving format.",
            adapter_status="candidate",
            owning_components=["doclift", "GroundRecall", "SciSiteForge"],
            access_constrained_default="metadata_only",
            adoption_notes="Index Kiwix-served or extracted content before native ZIM writing.",
        ),
        StandardRecord(
            standard_id="spdx",
            name="SPDX",
            steward="Linux Foundation",
            category="supply_chain",
            purpose="Software bill of materials and license metadata.",
            adapter_status="planned",
            owning_components=["Didactopus", "forge_guardrails"],
            access_constrained_default="metadata_only",
            adoption_notes="Use for appliance builds and pack-builder containers.",
        ),
        StandardRecord(
            standard_id="cyclonedx",
            name="CycloneDX",
            steward="OWASP",
            category="supply_chain",
            purpose="Software bill of materials for components and containers.",
            adapter_status="candidate",
            owning_components=["Didactopus", "forge_guardrails"],
            access_constrained_default="metadata_only",
            adoption_notes="Alternative or complement to SPDX for appliance builds.",
        ),
        StandardRecord(
            standard_id="sigstore",
            name="Sigstore-style artifact signing",
            steward="Sigstore project",
            category="artifact_integrity",
            purpose="Release and pack artifact signing.",
            adapter_status="candidate",
            owning_components=["Didactopus", "forge_guardrails"],
            access_constrained_default="metadata_only",
            adoption_notes="Add after checksummed pack capsules are stable.",
        ),
        StandardRecord(
            standard_id="scorm",
            name="SCORM",
            steward="ADL",
            category="legacy_lms",
            purpose="Legacy LMS content package compatibility.",
            adapter_status="legacy",
            owning_components=["Didactopus", "doclift"],
            access_constrained_default="disabled",
            adoption_notes="Legacy import/export only; not a primary Didactopus format.",
        ),
        StandardRecord(
            standard_id="lti",
            name="1EdTech Learning Tools Interoperability",
            steward="1EdTech",
            category="lms_launch",
            purpose="Launch and authentication integration with LMSs.",
            adapter_status="avoid_primary",
            owning_components=["Didactopus"],
            access_constrained_default="disabled",
            adoption_notes="Useful later for institutional launch, not offline learner baseline.",
        ),
    ]
    crosswalks = [
        crosswalk("DidactopusPack", "common_cartridge", "bidirectional", "lossy_export", "Didactopus", "metadata_only", "Course package boundary adapter."),
        crosswalk("PackCapsule", "spdx", "export", "lossy_export", "Didactopus", "metadata_only", "SBOM for appliance/container packaging, not pack semantics."),
        crosswalk("AssessmentItem", "qti", "bidirectional", "lossy_export", "Didactopus", "enabled_local_only", "Reviewed export; imported items enter draft review."),
        crosswalk("InteractiveAsset", "h5p", "import", "draft_import", "doclift", "metadata_only", "Recognize and index package metadata before runtime integration."),
        crosswalk("LearnerEvent", "xapi", "export", "lossy_export", "Didactopus", "disabled", "Optional local-only export; disabled in access-constrained profiles."),
        crosswalk("LearnerAnalyticsEvent", "caliper", "export", "future_candidate", "Didactopus", "disabled", "Institutional analytics only."),
        crosswalk("ConceptNode", "case", "bidirectional", "lossy_export", "GroundRecall", "metadata_only", "Reviewed external competency mapping."),
        crosswalk("ConceptNode", "skos_jsonld", "export", "lossy_export", "GroundRecall", "metadata_only", "Broader/narrower/related export where adequate."),
        crosswalk("PublicLearningPage", "schema_org_learning_resource", "export", "lossy_export", "SciSiteForge", "metadata_only", "Reviewed public metadata only."),
        crosswalk("SourceRecord", "w3c_prov", "export", "lossy_export", "GroundRecall", "metadata_only", "Canonical provenance summarized for exports."),
        crosswalk("CitationRecord", "csl_json", "bidirectional", "canonical", "CiteGeist", "metadata_only", "Citation interchange with source anchors."),
        crosswalk("LearnerPacket", "epub3", "export", "lossy_export", "Didactopus", "enabled_local_only", "Accessible offline study packet."),
        crosswalk("OfflineContentArchive", "openzim_zim", "import", "draft_import", "doclift", "metadata_only", "Index served/extracted content first."),
        crosswalk("PackCapsule", "sigstore", "export", "future_candidate", "forge_guardrails", "metadata_only", "Artifact signing after checksums."),
    ]
    return InteroperabilityRegistry(
        standards=standards,
        crosswalks=crosswalks,
        default_policy={
            "canonical_internal_format": "Didactopus pack capsule",
            "access_constrained_events": "local_only_by_default",
            "draft_imports": "must_enter_review_queue",
            "remote_routes": "disabled_unless_deliberately_configured",
        },
    )


def registry_payload() -> dict[str, Any]:
    registry = build_interoperability_registry()
    errors = registry.validate_crosswalk_targets()
    payload = registry.model_dump()
    payload["validation"] = {"ok": len(errors) == 0, "errors": errors}
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_pack_capsule_manifest(path: str | Path) -> PackCapsuleManifest:
    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return PackCapsuleManifest.model_validate(data)


def validate_pack_capsule(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        manifest = load_pack_capsule_manifest(manifest_path)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": [], "summary": {}}

    base = manifest_path.parent
    for entry in manifest.content_files:
        file_path = base / entry.path
        if entry.required and not file_path.exists():
            errors.append(f"Missing required content file: {entry.path}")
            continue
        if not file_path.exists():
            warnings.append(f"Optional content file is absent: {entry.path}")
            continue
        if not file_path.is_file():
            errors.append(f"Content path is not a file: {entry.path}")
            continue
        if entry.sha256:
            actual = _sha256(file_path)
            if actual != entry.sha256:
                errors.append(f"Checksum mismatch for {entry.path}: expected {entry.sha256}, got {actual}")

    registry = build_interoperability_registry()
    known_standards = set(registry.standards_by_id())
    for adapter in manifest.external_adapters:
        if adapter.standard_id not in known_standards:
            warnings.append(f"External adapter references unregistered standard: {adapter.standard_id}")
        if manifest.privacy_profile == "local_only" and adapter.standard_id in {"xapi", "caliper", "lti"}:
            warnings.append(f"{adapter.standard_id} adapter should stay disabled for local_only capsules unless explicitly reviewed")

    if not manifest.accessibility_features:
        warnings.append("No accessibility features declared.")
    if not manifest.model_requirements:
        warnings.append("No model requirements declared.")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "capsule_id": manifest.capsule_id,
            "pack_name": manifest.pack_name,
            "version": manifest.version,
            "review_status": manifest.review_status,
            "privacy_profile": manifest.privacy_profile,
            "content_file_count": len(manifest.content_files),
            "adapter_count": len(manifest.external_adapters),
            "warning_count": len(warnings),
            "error_count": len(errors),
        },
    }


def write_registry(out_path: str | Path) -> dict[str, Any]:
    payload = registry_payload()
    Path(out_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Didactopus interoperability helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)
    registry_parser = subparsers.add_parser("registry", help="Print the standards registry and crosswalk")
    registry_parser.add_argument("--out", help="Optional JSON output path")
    validate_parser = subparsers.add_parser("validate-capsule", help="Validate a pack capsule manifest JSON file")
    validate_parser.add_argument("manifest", help="Path to didactopus-pack-capsule manifest JSON")
    args = parser.parse_args()

    if args.command == "registry":
        payload = write_registry(args.out) if args.out else registry_payload()
        print(json.dumps(payload, indent=2))
        return
    if args.command == "validate-capsule":
        print(json.dumps(validate_pack_capsule(args.manifest), indent=2))


if __name__ == "__main__":
    main()
