# Visualization Notes

This repository now has two concrete visualization paths and a broader set of future UI ideas.

## Current implemented visualization

The MIT OCW Information and Entropy demo produces:

- `examples/ocw-information-entropy-run/learner_progress.svg`
- `examples/ocw-information-entropy-run/learner_progress.html`
- `examples/ocw-information-entropy-run/learner_progress_full_map.svg`
- `examples/ocw-information-entropy-run/learner_progress_full_map.html`

These are rendered by `didactopus.ocw_progress_viz`.

### Path-focused view

Shows:

- guided curriculum path
- mastered versus in-progress state
- per-concept mean evaluator score
- produced artifact name

### Full concept map

Shows:

- the same guided path in the center column
- side concepts grouped around their anchor lesson or prerequisite
- extractor spillover as informative context instead of hiding it

## Existing SVG/render helpers

The repository also includes generic SVG frame helpers in:

- `didactopus.export_svg`
- `didactopus.render_bundle`

Those are useful for frame-based graph rendering pipelines, but the OCW learner-progress visualizations are currently rendered directly as standalone SVG/HTML artifacts.

## Future UI directions

Useful next steps would be:

- pack DAG views with filtering by mastered/weak/noisy state
- review-workbench graph overlays
- stage-aware roadmap views
- side-by-side before/after review diffs
- animation or frame exports for learner progression over time
