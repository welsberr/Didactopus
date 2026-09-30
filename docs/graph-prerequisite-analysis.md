# Graph-Aware Prerequisite Analysis

This layer analyzes Didactopus packs as directed graphs over concept dependencies.

## Purpose

File validation asks whether a pack parses.
Structural validation asks whether pack artifacts agree.
Semantic QA asks whether a pack looks educationally plausible.
Graph-aware analysis asks whether the concept dependency structure itself looks healthy.

## Current checks

### Cycle detection
Flags direct or indirect prerequisite cycles.

### Isolated concept detection
Flags concepts with no incoming and no outgoing prerequisite edges.

### Direct prerequisite concentration
Flags concepts with at least three direct dependent concepts. The current count is
direct out-degree, not transitive descendants. This is an advisory review prompt,
not a claim that the concept is an educational bottleneck. The default threshold
has not been validated with instructors or learners.

### Flat-domain heuristic
Flags packs where there are too few prerequisite edges relative to concept count.

### Deep-chain heuristic
Flags long prerequisite chains that may indicate over-fragmentation.

## Output

Returns a status (`ok` or `invalid_input`), validation errors, warnings, exact
cyclic components, acyclic nodes downstream of cycles, and summary metrics. When
validation fails, analysis is marked `not_run` and graph warning count is null;
it must not be read as a clean graph. On a valid pack, analysis is marked
`complete`. Longest chain is unavailable for cyclic graphs rather than calculated
from an incomplete traversal.

These checks describe graph structure, not concept correctness, learning quality,
learner mastery, or causal change impact. A cycle in prerequisites needs review;
cycles in interaction workflows can be valid. Isolated concepts and sparse graphs
may also be intentional.

## Future work

- weighted edge confidence
- richer review views over strongly connected components and downstream blocked concepts
- pack-to-pack dependency overlays
- learner-profile-aware path complexity scoring
