# Multi-Source Ingestion

The multi-source ingestion layer lets Didactopus build one draft domain pack from
several heterogeneous inputs describing the same course or topic.

## Why this matters

Real course material is often scattered across:
- syllabus files
- lesson notes
- transcripts
- assignment sheets
- HTML pages
- supplemental markdown

A single-source parser is too narrow for serious curriculum distillation.

## Pipeline

1. detect adapter by file extension or naming convention
2. normalize each source into a `NormalizedSourceRecord`
3. merge sources into a `NormalizedCourse`
4. extract concept candidates
5. run rule-policy passes
6. emit merged draft pack
7. emit conflict report and attribution manifest

## Conflict report categories

- duplicate lesson titles across sources
- repeated key terms with different local contexts
- modules with no explicit exercises
- project-like content needing manual review
- lessons with thin mastery signals
