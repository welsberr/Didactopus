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

## Design requirements

Artifacts should be:
- human-readable
- diff-friendly
- versionable with Git
- independently licensed
- schema-validated
- mergeable and composable
- usable offline

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
