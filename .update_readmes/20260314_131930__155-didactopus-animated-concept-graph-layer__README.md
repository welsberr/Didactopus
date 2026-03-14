# Didactopus Animated Concept Graph Layer

This update extends the learning-animation scaffold with an **animated concept-graph view**.

## What it adds

- concept-graph playback frames
- node state transitions over time
- prerequisite edge rendering data
- API endpoint for graph animation payloads
- UI prototype for animated concept graph playback

## Why this matters

A bar-chart timeline is useful, but a concept graph better matches how Didactopus
represents mastery structure:

- concepts as nodes
- prerequisites as directed edges
- mastery progression as node color/size change
- availability/unlock state as a visible transition

This makes learning progression easier to interpret for:
- human learners
- AI-learner debugging
- curriculum designers
- reviewers comparing different runs

## Animation model

Each frame includes:
- node scores
- node status (`locked`, `available`, `active`, `mastered`)
- simple node size hints derived from score
- static prerequisite edges

Later versions could add:
- force-directed layouts
- semantic cross-pack links
- edge highlighting when prerequisite satisfaction changes
- side-by-side learner comparison
