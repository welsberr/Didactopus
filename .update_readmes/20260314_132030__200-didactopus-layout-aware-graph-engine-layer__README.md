# Didactopus Layout-Aware Graph Engine Layer

This update extends the animated concept-graph scaffold with a **layout-aware graph engine**.

## What it adds

- stable node positioning
- pack-authored coordinates
- automatic layered layout fallback
- cross-pack concept links
- SVG frame export scaffolding
- UI prototype with stable animated graph playback

## Why this matters

Animated concept graphs are much more readable when node positions do not jump around.
This layer makes the graph a more faithful representation of a mastery ecosystem by adding:

- deterministic coordinates
- prerequisite layering
- optional author-specified placement
- cross-pack links for broader learning pathways
- export-ready frame generation for later GIF/MP4 pipelines

## Layout model

The engine uses this priority order:

1. explicit pack-authored coordinates
2. automatic layered layout from prerequisite depth
3. deterministic horizontal spacing inside each depth layer

## Export model

This scaffold includes:
- graph frame payloads from the API
- SVG frame export helper script
- one SVG per frame for later conversion to GIF/MP4 with external tools

## Strong next step

- force-directed refinement
- edge highlighting on unlock transitions
- cross-pack supergraph views
- direct GIF/MP4 rendering pipeline
