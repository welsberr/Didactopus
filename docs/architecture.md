# Architecture Overview

## System aim

Didactopus supports mastery-oriented autodidactic learning across many domains while reducing the risk that AI becomes a crutch for superficial performance.

## Top-level architecture

```text
Learner Interface
    |
    v
Orchestration Layer
    |- learner profile
    |- session state
    |- competency tracker
    |- artifact registry
    |
    +--> Domain Mapping Engine
    +--> Curriculum Generator
    +--> Mentor Agent
    +--> Practice Generator
    +--> Project Advisor
    +--> Evaluation System
    |
    v
Model Provider Abstraction
    |- local model backends
    |- optional remote backends
```

## Core data objects

- **LearnerProfile**: goals, prior knowledge, pacing, artifacts, assessment history
- **ConceptNode**: concept, prerequisites, representative tasks, mastery criteria
- **RoadmapStage**: stage goals, concepts, practice forms, project milestones
- **EvidenceItem**: explanations, solved problems, project artifacts, benchmark scores
- **EvaluationReport**: rubric scores, weaknesses, suggested remediation
- **ArtifactManifest**: metadata for a domain pack or other contributed artifact

## Critical design constraint

The platform should optimize for **competence evidence** rather than conversational fluency. A learner should not advance based solely on sounding knowledgeable.

## Local-first inference

The provider abstraction should support:
- Ollama
- llama.cpp HTTP servers
- LM Studio local server
- vLLM or comparable self-hosted inference
- optional remote APIs only by explicit configuration

For access-constrained deployments, local-first must also mean:

- no telemetry, cloud sync, crash upload, or remote model route by default;
- clear labeling before any external route is used;
- local-only learner ledgers unless deliberately exported;
- minimal learner identity requirements;
- pack and model health checks that a local steward can understand;
- no promise that application settings alone provide secrecy or safety in
  hostile environments.

## Artifact ecosystem

The architecture should support:
- first-party curated packs
- third-party domain packs
- version validation
- compatibility checks
- offline local discovery
- offline pack capsules with checksums or signatures
- low-bandwidth and removable-media distribution

## Safety against shallow learning

The orchestration layer should support policies such as:
- forcing first-attempt learner answers
- hiding worked solutions until after effort is shown
- requiring self-explanation
- issuing counterexamples and adversarial probes
- cross-checking claims against references and experiments where applicable
