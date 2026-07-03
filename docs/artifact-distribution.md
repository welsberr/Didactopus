# Artifact Distribution Plan

## Goal

Didactopus should support community-contributed, versioned learning artifacts that can be reused, extended, and distributed independently of the core codebase.

## Artifact classes

The platform should support distribution of:
- domain plans
- concept graphs
- roadmap templates
- exercise banks
- project blueprints
- rubrics
- benchmark tasks
- reference reading lists
- exemplar work products

## Distribution models

### 1. In-repository packs
Simple packs stored under `domain-packs/` for development, examples, and curated first-party artifacts.

### 2. External Git repositories
A contributor can publish a domain pack as its own Git repository and users can clone or vendor it.

Didactopus can also use an external Git repository as a source-material repository rather than only as a finished pack repository. The recommended pattern is one repository per course, with a root `didactopus-course.yaml` manifest plus a local source tree and `sources.yaml`.

Example patterns:
- `didactopus-pack-statistics`
- `didactopus-pack-electronics`
- `didactopus-pack-evolutionary-biology`
- `didactopus-mit-ocw-6-050j`

### 3. Package index model
Eventually, packs could be distributed through a registry or package index. A manifest should identify:
- pack name
- version
- author
- license
- compatible Didactopus versions
- dependencies on other packs or shared competencies

### 4. Offline pack capsules
Access-constrained deployments need packs that can be moved by archive file,
removable media, or local mirror without requiring Git or continuous internet
access. A pack capsule should include:

- pack manifest;
- source, concept, practice, answer-key, and coverage artifacts;
- license and redistribution metadata;
- language and accessibility metadata;
- model and hardware requirements;
- review status and provenance;
- checksums, and signatures when signing infrastructure is available;
- printable learner and steward guides.

Pack capsules remain the canonical Didactopus distribution unit. External
standards should be boundary adapters, not replacements for the internal pack
model. The first useful adapters are:

- Common Cartridge for LMS/course exchange;
- QTI for reviewed assessment item exchange;
- EPUB for portable learner guides;
- ZIM/static web bundles for offline libraries and local mirrors;
- H5P package metadata for interactive practice assets;
- xAPI export for optional local learner-event interchange.

The adoption plan is tracked in
[interoperability-and-feature-adoption.md](interoperability-and-feature-adoption.md).

The first manifest fixture is under
`examples/pack-capsule-example/didactopus-pack-capsule.json`. Validate it with:

```bash
PYTHONPATH=src python -m didactopus.main pack-capsule-validate examples/pack-capsule-example/didactopus-pack-capsule.json
```

## Design requirements

Artifacts should be:
- human-readable
- diff-friendly
- versionable with Git
- independently licensed
- schema-validated
- mergeable and composable
- usable offline
- importable without expert configuration
- verifiable by checksum or signature where possible

## Recommended file formats

Use YAML or JSON for:
- metadata
- concept graphs
- roadmap stages
- projects
- rubrics

Use Markdown for:
- explanatory notes
- contributor guidance
- reading guides
- learner-facing instructions

## Versioning

Each pack should declare:
- semantic version
- minimum core version
- maximum tested core version, if needed
- schema version

## Future extension

Later, Didactopus should support:
- signed packs
- dependency resolution
- artifact provenance metadata
- import/export CLI commands
- trust policies for third-party packs
- low-bandwidth update bundles
- local mirror and removable-media workflows
