# Confidence overhaul

Didactopus now treats legacy `confidence` and `confidence_hint` values as scoped confidence signals instead of generic truth or mastery scores.

## Inventory contract

`docs/confidence-inventory.json` is the checked-in inventory of production confidence fields under `src/didactopus`. The regression test in `tests/test_confidence_overhaul.py` regenerates the inventory and fails if a new confidence occurrence appears without an explicit classification.

Current classifications distinguish learner-state mastery, graph extraction fidelity, citation extraction hints, candidate extraction hints, GroundRecall bridge fields, benchmark response probabilities, and confidence contract tooling.

## API and database semantics

For absence-meaningful values, missing confidence is now represented as `null`/`None`, not `0.0`.

- `KnowledgeCandidateCreate.confidence_hint` is optional and bounded to `[0.0, 1.0]`.
- `KnowledgeCandidateCreate.confidence_assessments` carries typed assessment payloads while preserving the legacy `confidence_hint` API field.
- `MasteryRecord.confidence` is optional and bounded to `[0.0, 1.0]`.
- `KnowledgeCandidateORM.confidence_hint` and `MasteryRecordORM.confidence` are nullable.
- `KnowledgeCandidateORM.confidence_assessments_json` stores additive typed assessments.

This preserves the distinction between “not assessed” and an explicit zero-confidence assessment.

## Typed extraction assessments

Knowledge-candidate and citation extraction hints are converted to Epistemap-compatible `ConfidenceAssessment` records with:

- `dimension = "extraction_fidelity"`
- stable policy IDs:
  - `didactopus_candidate_extraction_hint.v1`
  - `didactopus_citation_extraction_hint.v1`
- stable basis hashes over source/candidate identifiers
- metadata flags noting that the assessment is not learner mastery and not source truth

Graph edges already expose structural extraction confidence as `extraction_fidelity` with rationale text that distinguishes it from learner mastery and claim truth.

## SQLite migration

Run the additive migration with:

```bash
python -m didactopus.confidence path/to/didactopus.sqlite --report confidence-migration-report.json
python -m didactopus.confidence path/to/didactopus.sqlite --apply --report confidence-migration-report.json
```

Dry runs report intended operations without modifying the database. Applied runs add `knowledge_candidates.confidence_assessments_json` if missing and append typed assessments for non-zero legacy `confidence_hint` values.

Legacy `0.0` values are reported with `code = "legacy_zero_ambiguous"` and are not automatically converted, because old database rows cannot prove whether zero meant “explicit zero confidence” or “missing/defaulted confidence.” New API and ORM round trips preserve explicit zero distinctly from missing values.

## GroundRecall bridge

Notebook-page generation preserves GroundRecall `confidence_profile` payloads without flattening them into Didactopus scalar confidence fields.
