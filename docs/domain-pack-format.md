# Domain Pack Format

## Purpose

A domain pack is the primary distributable artifact for Didactopus. It contains structured material describing a field, learning sequence, projects, and evaluation artifacts.

## Directory layout

```text
example-pack/
├── pack.yaml
├── concepts.yaml
├── roadmap.yaml
├── projects.yaml
├── rubrics.yaml
├── resources.md
└── LICENSE
```

## pack.yaml

The manifest should contain:
- pack name
- display name
- version
- schema version
- description
- author
- license
- tags
- didactopus compatibility
- optional dependencies

## concepts.yaml

Contains:
- concept identifiers
- descriptions
- prerequisites
- representative tasks
- mastery signals

## roadmap.yaml

Contains:
- stages
- stage goals
- concept clusters
- checkpoint criteria
- recommended pacing notes

## projects.yaml

Contains:
- project identifiers
- difficulty
- prerequisites
- deliverables
- milestone suggestions
- verification expectations

## rubrics.yaml

Contains:
- assessment criteria
- score bands
- explanation requirements
- transfer-task criteria

## Example philosophy

The pack format should separate:
- domain structure
- learning sequence
- authentic practice
- evidence standards

That separation makes contributed packs easier to compare, merge, and improve.
