# Component Specifications

## Domain Mapping Engine
Inputs:
- selected domain
- learner goal
- optional prior knowledge notes
- optional domain pack

Outputs:
- concept graph
- prerequisite chains
- competency clusters
- recommended sequence

## Curriculum Generator
Inputs:
- concept graph
- learner profile
- assessment results
- roadmap templates from pack

Outputs:
- roadmap stages
- study sessions
- mastery checkpoints
- recommended projects

## Mentor Agent
Responsibilities:
- ask probing questions
- request justification
- detect vague understanding
- encourage verification
- avoid over-answering

## Practice Generator
Responsibilities:
- generate exercises by concept
- vary difficulty and modality
- create transfer tasks
- produce reflection prompts

## Project Advisor
Responsibilities:
- suggest authentic projects
- decompose milestones
- help define success criteria
- review artifacts

## Evaluation System
Responsibilities:
- assess correctness
- assess explanation quality
- assess transfer and robustness
- recommend remediation

## Artifact Registry
Responsibilities:
- discover local domain packs
- validate manifests
- check compatibility
- expose installed artifacts to the orchestration layer
