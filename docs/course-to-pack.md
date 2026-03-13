# Course-to-Pack Ingestion Pipeline

The course-to-pack pipeline transforms educational material into Didactopus-native artifacts.

## Inputs

Typical sources:
- syllabus text
- lesson outlines
- markdown notes
- HTML course pages
- assignment sheets
- quiz prompts
- lecture transcripts

## Normalized intermediate structure

The pipeline builds a `NormalizedCourse` object containing:
- title
- source metadata
- modules
- lessons
- learning objectives
- exercises
- key terms
- project prompts

## Rule-policy adapter

The pipeline includes a small rule layer for stable policy transforms such as:
- suggest prerequisites from ordering
- merge repeated key-term candidates
- flag modules with no exercises
- flag concepts with weak evidence of distinctness
- suggest project concepts from capstone markers
