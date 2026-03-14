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

### Bottleneck detection
Flags concepts with unusually many downstream dependents.

### Flat-domain heuristic
Flags packs where there are too few prerequisite edges relative to concept count.

### Deep-chain heuristic
Flags long prerequisite chains that may indicate over-fragmentation.

## Output

Returns:
- graph warnings
- summary counts
- structural graph metrics

## Future work

- weighted edge confidence
- strongly connected component summaries
- pack-to-pack dependency overlays
- learner-profile-aware path complexity scoring
