# Didactopus Direct Media Rendering Pipeline Layer

This update extends the layout-aware graph engine with a **direct media-rendering pipeline**
for turning learning animations into shareable artifacts.

## What it adds

- SVG frame export integration
- GIF manifest generation
- MP4 manifest generation
- FFmpeg-oriented render script scaffolding
- API endpoint for media render jobs
- UI prototype for creating export bundles

## Why this matters

Didactopus should not stop at interactive playback. It should also be able to produce
portable visual artifacts for:

- research presentations
- learner progress sharing
- curriculum review
- AI learner debugging
- repository documentation

This layer provides a structured path from graph animation payloads to:
- frame directories
- render manifests
- GIF/MP4-ready job bundles

## Scope

This scaffold produces:
- exported SVG frames
- JSON render manifests
- shell script scaffolding for FFmpeg conversion

It does **not** embed FFmpeg execution into the API server itself.
That is a deliberate separation so rendering can be delegated to a worker or offline job.

## Strong next step

- actual worker-backed render execution
- render status tracking
- downloadable media artifact registry
- parameterized themes, sizes, and captions
