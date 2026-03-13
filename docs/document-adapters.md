# Document Adapters

Didactopus now includes adapter scaffolds for several common educational document types.

## Supported adapter interfaces

- PDF adapter
- DOCX adapter
- PPTX adapter
- HTML adapter
- Markdown adapter
- text adapter

## Current status

The current implementation is intentionally conservative:
- it focuses on stable interfaces
- it extracts text in a simplified way
- it normalizes results into shared internal structures

## Why this matters

Educational material commonly lives in:
- syllabi PDFs
- DOCX notes
- PowerPoint slide decks
- LMS HTML exports
- markdown lesson files

A useful curriculum distiller must be able to treat these as first-class inputs.

## Adapter contract

Each adapter returns a normalized document record with:
- source path
- source type
- title
- extracted text
- sections
- metadata

This record is then passed into higher-level course/topic distillation logic.
