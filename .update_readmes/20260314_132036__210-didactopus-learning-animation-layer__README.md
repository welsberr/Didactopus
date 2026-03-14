# Didactopus Run/Session Correlation + Learning Animation Layer

This update extends the agent audit / key rotation scaffold with:

- **run/session correlation** for learner episodes
- **workflow logs** tied to learner runs
- **animation data endpoints** for replaying learning progress
- a **UI prototype** that can animate a learner's mastery changes over time

## Why this matters

A single audit event is useful, but it does not tell the full story of a learning episode.

For both human learners and AI learners, Didactopus should be able to represent:

- when a learning run began
- what sequence of actions happened
- how mastery estimates changed during the run
- how recommendations shifted as competence improved

That makes it possible to:
- inspect learner trajectories
- debug agentic learning behavior
- demonstrate the learning process to users, reviewers, or researchers
- create visualizations and animations of learning over time

## Added in this scaffold

- learner run/session records
- workflow event log records
- animation frame generation from learner history
- API endpoints for run creation, workflow-event logging, and animation playback data
- UI prototype for replaying learning progression as an animation

## Animation concept

This scaffold uses a simple time-series animation model:
- each frame corresponds to a learner-history event
- each concept's mastery score is shown per frame
- the UI can replay those frames with a timer

Later implementations could support:
- graph/network animation
- concept unlock transitions
- recommendation timeline overlays
- side-by-side human vs AI learner comparison
