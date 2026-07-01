# Interoperability And Feature Adoption Plan

Didactopus should borrow mature patterns from existing learning systems without
turning into a conventional LMS. Its distinctive role remains source-grounded
mentoring, practice, evaluation, and mastery evidence. Interoperability should
make that role easier to deploy with existing content, offline platforms,
institutional systems, and public site outputs.

## Adoption Priorities

### 1. Offline Content And Appliance Patterns

Useful systems:

- Kolibri: offline-first learning platform, content library, teacher/coach
  workflows, Android app, local classroom server, external-storage and
  peer-to-peer distribution.
- Kiwix/openZIM: offline web content in ZIM files, local reader/server, strong
  precedent for offline knowledge access.
- Internet-in-a-Box: Raspberry Pi or local hotspot model that aggregates Kiwix,
  OER2Go/RACHEL-style content, maps, LMS apps, and local services.

Didactopus adoption:

- Treat Kolibri/Kiwix/Internet-in-a-Box as compatible deployment neighbors, not
  competitors.
- Add import adapters for ZIM catalogs, Kiwix-served content, and static web
  bundles into doclift/GroundRecall.
- Add optional Didactopus pack capsules that can be distributed by removable
  media and installed by a steward without Git.
- Add a "mentor overlay" pattern: Didactopus can index a local offline content
  library, then provide source-grounded mentoring, retrieval practice, and
  mastery evidence over it.
- Avoid duplicating Kiwix or Internet-in-a-Box hotspot management unless a
  Didactopus-specific learner appliance needs a narrow wrapper.

### 2. Course And Assessment Interchange

Useful standards:

- 1EdTech Common Cartridge for course/package exchange.
- 1EdTech QTI for assessment item and test interchange.
- H5P for reusable interactive HTML5 learning activities.
- Moodle XML and GIFT only as pragmatic legacy/import targets where needed.

Didactopus adoption:

- Keep the Didactopus pack capsule as the canonical internal format.
- Add Common Cartridge import/export as a boundary adapter for LMS/course
  exchange.
- Add QTI export for reviewed practice prompts, quizzes, and answer-keyed
  assessment items.
- Add QTI import into a draft review queue rather than immediate trusted
  mastery material.
- Treat H5P packages as interactive assets that can be indexed, linked, and
  optionally launched; export to H5P only for simple stable interaction types.

### 3. Learning Events And Mastery Evidence

Useful standards:

- xAPI for learner activity statements and local Learning Record Store patterns.
- 1EdTech Caliper for analytics events in institutional environments.
- 1EdTech Comprehensive Learner Record and Open Badges for portable achievement
  claims.

Didactopus adoption:

- Define a local-only Didactopus learning event stream first.
- Provide an optional xAPI export profile for learner attempts, feedback,
  retrieval practice, assessment results, and retention checks.
- Keep xAPI/Caliper export disabled by default in access-constrained profiles.
- Add privacy-preserving aggregation before any multi-learner analytics.
- Export CLR/Open Badges only from reviewed mastery evidence and only after
  explicit learner/steward action.

### 4. Competency And Concept Alignment

Useful standards:

- 1EdTech CASE for academic standards and competency identifiers.
- SKOS/JSON-LD for concept schemes and broader/narrower/related relations.
- Schema.org `Course` and `LearningResource` for public educational metadata.

Didactopus adoption:

- Keep the concept graph internal model, but add a mapping layer for external
  competency IDs.
- Store mappings as reviewed claim-alignment records with positive and negative
  evidence, not as forced one-to-one aliases.
- Export public SciSiteForge pages with Schema.org JSON-LD for courses,
  learning resources, FAQs, and educational articles.
- Use SKOS-style concept relation vocabulary for cross-pack exports where it
  does not weaken the richer Didactopus graph.

### 5. Provenance, Citation, And Knowledge Substrate

Useful standards:

- W3C PROV for entity/activity/agent provenance.
- PAV-style authoring/versioning distinctions where useful.
- Dublin Core, CSL-JSON, BibTeX/BibLaTeX, DOI, ORCID, and related bibliographic
  identifiers for citation workflows.
- RO-Crate or BagIt-style packaging as possible future corpus/package
  distribution options.

Stack adoption:

- GroundRecall should own canonical provenance and review state.
- doclift should emit stable source, extraction, transformation, and chunk
  provenance.
- CiteGeist should own citation-normalization exports such as CSL-JSON and
  BibTeX/BibLaTeX.
- SciSiteForge should publish only reviewed, public-safe provenance summaries.
- Didactopus should consume provenance for learner-facing source support and
  evaluator feedback.

### 6. Accessibility And Offline Reading

Useful standards:

- WCAG 2.2 as the baseline for web learner surfaces.
- EPUB 3 for portable learner guides and offline reading.
- HTML plus ARIA where the learner interface needs browser-native access.

Didactopus adoption:

- Treat WCAG 2.2 AA as the default target for learner-facing web surfaces.
- Generate accessible HTML and EPUB study packets from reviewed packs.
- Keep printable and text-only views available for access-constrained
  deployments.
- Add accessibility metadata to pack capsules and Common Cartridge exports.

### 7. Supply-Chain And Pack Integrity

Useful standards and tools:

- SPDX and CycloneDX for bills of materials.
- Sigstore or equivalent signing for release and pack artifacts.
- SLSA-style provenance levels as a maturity model for release pipelines.

Didactopus adoption:

- Add checksums to every pack capsule first.
- Add signed pack manifests when release infrastructure is ready.
- Emit SBOMs for learner appliance builds and pack-builder containers.
- Store model identity, quantization, license, and source in model-capability
  manifests, then include those in benchmark and deployment reports.

## Stack Allocation

Didactopus:

- pack capsule schema and validation;
- Common Cartridge and QTI boundary adapters;
- learner event stream and optional xAPI export;
- mastery-ledger export to CLR/Open Badges when reviewed;
- accessible learner HTML/EPUB views;
- steward-facing install and readiness workflows.

GroundRecall:

- canonical source, concept, claim, provenance, review, and public/private
  policy records;
- W3C PROV/PAV-oriented export layer;
- SKOS/JSON-LD concept and relation exports;
- restricted-source and publication-safety checks.

doclift:

- ingestion adapters for EPUB, ZIM/static web archives, Common Cartridge, QTI,
  H5P package metadata, and existing source bundles;
- extraction provenance and role/hint records for downstream review.

CiteGeist:

- citation normalization and export through CSL-JSON, BibTeX/BibLaTeX, DOI,
  ORCID, and related identifiers;
- support mapping from citation records to Didactopus source anchors and
  GroundRecall provenance.

SciSiteForge:

- Schema.org JSON-LD for public educational resources;
- reviewed study-aid and source-spine publication;
- optional ZIM/static bundle export for offline mirrors;
- public search indexes that exclude restricted and unreviewed material.

GenieHive:

- local model route manifests;
- role adequacy and health reporting;
- model license, size, quantization, context, and benchmark metadata for offline
  learner appliance profiles.

Forge guardrails:

- checks that pack exports do not leak restricted Library material;
- checks that xAPI/Caliper/analytics exports are disabled in private/offline
  profiles unless deliberately enabled;
- checks that generated public pages include provenance and machine-readable
  metadata only at the reviewed publication level.

## Implementation Roadmap

### Phase 1. Standards Registry And Crosswalk

- Create a machine-readable registry of supported standards and adapter status.
- Map Didactopus internal objects to external standards:
  `Pack -> Common Cartridge`, `AssessmentItem -> QTI`, `LearnerEvent -> xAPI`,
  `ConceptNode -> CASE/SKOS`, `MasteryEvidence -> CLR/Open Badges`,
  `SourceRecord -> PROV/CSL`.
- Mark each mapping as `canonical`, `lossy_export`, `draft_import`, or
  `future_candidate`.

Implemented scaffold:

```bash
PYTHONPATH=src python -m didactopus.main interoperability-registry
```

This emits the current standards registry, stack ownership, access-constrained
defaults, internal-object crosswalks, and registry validation result.

### Phase 2. Pack Capsule Manifest v0

- Define the pack capsule manifest with content files, checksums, license,
  language, accessibility metadata, model requirements, review status, and
  provenance summary.
- Add validation and plain-language error output for stewards.
- Support local archive import/export before network registry work.

Implemented scaffold:

```bash
PYTHONPATH=src python -m didactopus.main pack-capsule-validate examples/pack-capsule-example/didactopus-pack-capsule.json
```

The v0 validator checks required content files, declared SHA-256 checksums,
local-only privacy defaults, registered external adapter identifiers, declared
accessibility features, and model requirements. It intentionally validates
capsule metadata and local safety posture before implementing archive import or
signing.

### Phase 3. Assessment And Practice Interchange

- Implement QTI export for reviewed true/false, multiple-choice, short-answer,
  and rubric-backed practice where the mapping is reliable.
- Implement QTI import into draft review packs.
- Add H5P package recognition and asset indexing.
- Add a later H5P export path only for simple stable practice activities.

### Phase 4. Offline Content Adapters

- Add doclift/GroundRecall ingestion support for EPUB and static HTML bundles.
- Add ZIM/Kiwix catalog support, initially by indexing metadata and content
  served through `kiwix-serve` or extracted static content.
- Add SciSiteForge static/ZIM export planning for public-safe educational
  bundles.

### Phase 5. Local Learning Event Stream

- Define Didactopus learner events with privacy labels.
- Add local-only event storage for attempts, feedback, retrieval practice,
  assessment, and retention.
- Add optional xAPI export profile and a disabled-by-default local LRS bridge.
- Consider Caliper only for institutional integration, not for the offline
  access-constrained baseline.

### Phase 6. Public Metadata And Site Integration

- Add Schema.org JSON-LD generation for SciSiteForge educational pages.
- Add pack metadata export to Common Cartridge where a site section maps to a
  course/module.
- Add public-search facets for concept, source type, review status, and
  educational level.

### Phase 7. Integrity And Release Hardening

- Add checksums to pack capsule exports.
- Add SPDX or CycloneDX SBOM generation for learner appliance builds.
- Add artifact signing for pack capsules and release bundles.
- Add steward-facing verification output before installing a pack.

## Standards To Avoid As Primary Formats

- SCORM should be treated as legacy compatibility only. It is useful for old LMS
  content but too narrow for Didactopus mentoring, local privacy, and
  source-grounded evidence needs.
- LTI should not be part of the offline learner baseline. It is useful later
  when Didactopus needs to launch inside Moodle, Open edX, Canvas, or another
  LMS, but it assumes institutional integration and web authentication.
- Caliper should not be enabled by default. It is useful for institutional
  analytics, but access-constrained deployments should default to local-only
  private event storage.
