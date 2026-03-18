# Multilingual QA

Didactopus now supports an optional per-pack multilingual QA spec.

The goal is not to certify perfect translation quality. The goal is to make multilingual evaluation less dependent on vague fluency judgments by checking whether key terms, caveats, and forbidden confusions survive across languages.

## Spec File

Place this file in a pack directory:

- `multilingual_qa.yaml`

It is currently optional.

## Current Shape

```yaml
source_language: en
targets:
  es:
    required_terms:
      - id: shannon-entropy
        round_trip_required: true
        round_trip_source: "Shannon entropy"
        accepted:
          - "entropía de shannon"
    required_caveats:
      - id: shannon-vs-thermo-not-identical
        round_trip_required: true
        round_trip_source: "Shannon entropy is not identical to thermodynamic entropy"
        accepted:
          - "no es idéntica"
    forbidden_confusions:
      - id: shannon-equals-thermodynamic-entropy
        patterns:
          - "es idéntica a la entropía termodinámica"
```

Use `round_trip_source` for the reviewer-approved source-language phrase that should remain recoverable after back-translation. That is better than using the first target-language phrase mechanically.

## Starter Generation

Didactopus can now generate a draft starter spec for reviewer refinement:

```bash
python -m didactopus.multilingual_qa_seed domain-packs/mit-ocw-information-entropy \
  --out domain-packs/mit-ocw-information-entropy/multilingual_qa.seed.yaml \
  --languages es fr
```

The generated `multilingual_qa.seed.yaml` is not meant for immediate trust. It is a reviewer aid that pulls:

- multi-word concept titles as draft required terms
- likely caveat candidates from grounded source fragments
- likely forbidden confusions derived from negated caveat language

## Promotion Tooling

Didactopus can now promote selected seed entries into a curated spec:

```bash
python -m didactopus.multilingual_qa_review \
  --seed domain-packs/mit-ocw-information-entropy/multilingual_qa.seed.yaml \
  --out domain-packs/mit-ocw-information-entropy/multilingual_qa.yaml \
  --language es \
  --required-term-id shannon-entropy \
  --required-term-id channel-capacity \
  --required-caveat-id shannon-vs-thermo-not-identical \
  --forbidden-confusion-id shannon-equals-thermodynamic-entropy \
  --canonical-round-trip-id shannon-entropy \
  --canonical-round-trip-id shannon-vs-thermo-not-identical
```

This is meant to reduce manual editing by letting a reviewer:

- choose which seed entries to keep
- mark which entries should drive canonical round-trip checks
- merge selected entries into the curated `multilingual_qa.yaml`

## What It Checks

For a target language, the QA layer can check:

- required terms that should appear in acceptable translated or multilingual output
- required caveats that must survive explanation
- forbidden confusions that should trigger warnings

## Where It Is Used

This spec now feeds:

- the local model benchmark
- the Didactopus arena

Those tools still use heuristic scoring, but multilingual QA spec checks now contribute an explicit preservation signal.

## Why This Helps

This gives Didactopus a better layered multilingual evaluation model:

1. language-alignment heuristics
2. term and caveat preservation checks
3. round-trip warning checks on required phrases
4. arena comparison and LLM review support
5. human bilingual review for promoted or disputed outputs

## Current Limitation

This is still a lightweight preservation framework. It does not yet prove semantic equivalence across whole explanations. It is best treated as an early QA filter and promotion aid.
