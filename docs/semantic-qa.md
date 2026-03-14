# Semantic QA Layer

The semantic QA layer sits above structural validation.

## Purpose

Structural validation tells us whether a pack is syntactically and referentially
coherent. Semantic QA asks whether it also looks *educationally plausible*.

## Current checks

### Near-duplicate title check
Flags concept titles that are lexically very similar.

### Over-broad concept check
Flags titles that look unusually broad or compound, such as:
- "Prior and Posterior"
- "Statistics and Probability"
- "Modeling and Inference"

### Description similarity check
Flags concepts whose descriptions appear highly similar.

### Missing bridge concept check
Looks at successive roadmap stages and flags abrupt jumps where later stages do
not seem to share enough semantic continuity with earlier stages.

### Thin prerequisite chain check
Flags advanced-sounding concepts that have zero or very few prerequisites.

## Output

Semantic QA returns:
- warnings
- summary counts
- finding categories

## Future work

- embedding-backed similarity
- prerequisite cycle suspicion scoring
- topic-cluster coherence
- cross-pack semantic overlap
- domain-specific semantic QA plugins
