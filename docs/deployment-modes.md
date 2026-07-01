# Deployment Modes

This document defines the intended boundary between `Didactopus`, `GroundRecall`, and `GenieHive` across the main deployment/use-case modes now visible in the project.

It exists to prevent accidental architectural drift while the code still lives in one repository.

## Layer Roles

### Didactopus

Primary role:

- learner-facing application
- pack and curriculum workflows
- mentoring, practice, evaluation, and review experiences

It should own capabilities whose value depends on:

- a learner or team of learners
- a study path or mastery target
- pedagogical sequencing
- educational review and promotion workflows

### GroundRecall

Primary role:

- grounded knowledge substrate
- `llmwiki++` successor
- canonical claim, concept, relation, artifact, and provenance layer

It should own capabilities whose value remains even when there is:

- no learner
- no curriculum pack
- no educational session
- no Didactopus UI

That includes:

- general knowledge ingestion
- canonical promotion and query
- assistant-neutral export
- sync and merge
- shared knowledge operations

### GenieHive

Primary role:

- model and service routing layer
- provider inspection and route resolution
- runtime capability selection across local or clustered AI services

It should not own educational semantics or canonical knowledge semantics.

## Deployment Modes

### 1. Learner Node

Composition:

- `Didactopus`
- `GroundRecall`
- optional `GenieHive`

Primary user:

- individual learner
- tutor/mentor workflow operator

Main jobs:

- ingest or consume prepared learning resources
- run mentor/practice/evaluator loops
- inspect grounded source support
- keep local grounded knowledge available to the learner workflow

Boundary implication:

- `Didactopus` is the entry point and continuing interface
- `GroundRecall` is a supporting substrate
- `GenieHive` is a supporting routing layer

CLI implication:

- learner-facing and review-workflow commands can live under `didactopus`
- GroundRecall commands may be present locally but are not the primary user interface

### 2. Access-Constrained Learner Node

Composition:

- `Didactopus`
- `GroundRecall`
- local model route through `GenieHive`, Ollama, llama.cpp, or equivalent
- curated offline learning packs
- optional steward dashboard or simple operator CLI

Primary user:

- learner without reliable access to teachers, tutors, cloud services, or safe
  institutional education
- local steward maintaining a device, LAN node, or removable-media pack library

Main jobs:

- run source-grounded mentoring without requiring human tutors
- operate offline or with explicitly configured remote routes only
- preserve learner privacy by default
- make setup, health checks, pack installation, and basic recovery feasible for
  a non-specialist steward
- support low-bandwidth and removable-media pack distribution

Boundary implication:

- `Didactopus` owns the learner and steward experience
- `GroundRecall` owns the local knowledge, source, provenance, and pack
  substrate
- `GenieHive` owns model route selection and local/cluster service health
- security-sensitive deployment guidance must avoid promising secrecy or safety
  in hostile environments

Required maturity:

- no default telemetry or automatic remote calls
- local-only learner ledgers by default
- explicit labeling of remote model or retrieval routes
- signed or checksummed pack capsules when distribution infrastructure exists
- plain-language readiness and maintenance checks

CLI implication:

- basic learner-node setup should not require editing configuration files
- ordinary steward operations should have a simple command or UI path
- advanced GroundRecall and GenieHive commands may remain available for expert
  maintainers

Reference:

- [access-constrained-mentoring.md](access-constrained-mentoring.md)

### 3. Knowledge Node

Composition:

- `GroundRecall`
- optional `GenieHive`
- no `Didactopus` required

Primary user:

- `llmwiki++` user
- individual researcher
- local knowledge curator

Main jobs:

- ingest notes, transcripts, wiki trees, packs, and corpora
- normalize claims, concepts, relations, and provenance
- run review, promotion, query, and export
- maintain assistant-neutral knowledge state

Boundary implication:

- `GroundRecall` must be usable without learner-specific Didactopus features
- if a capability is required for this node and does not depend on pedagogy, it belongs in GroundRecall

CLI implication:

- GroundRecall should grow toward its own first-class CLI surface
- Didactopus should not be the permanent home for generic knowledge-OS commands

### 4. Team Knowledge Node

Composition:

- `GroundRecall`
- optional `GenieHive`
- optional `Didactopus` for some users

Primary user:

- team members maintaining individual and shared grounded knowledge

Main jobs:

- preserve private and shared knowledge scopes
- merge promoted knowledge across users and machines
- resolve contradictions, supersessions, and review state
- export assistant-neutral bundles for multiple tools

Boundary implication:

- team/shared knowledge merger is a GroundRecall responsibility
- Didactopus may consume the shared substrate, but should not be the required coordination layer

Required GroundRecall maturity:

- canonical store durability
- review and promotion
- sync and merge semantics
- provenance and author/machine identity
- assistant-neutral exports

### 5. Corpus Transformation Node

Composition:

- one or more `GroundRecall` instances
- optional `GenieHive`
- `Didactopus` optional for human review tasks only

Primary user:

- operator transforming large unstructured corpora into grounded integrated knowledge

Main jobs:

- parallel ingestion of weakly structured materials
- extraction and normalization
- contradiction/supersession handling
- full knowledge merger and promotion
- consolidated export

Boundary implication:

- this is strongly a GroundRecall problem, not a Didactopus-first one
- Didactopus may assist with review or educational packaging after consolidation

Architectural consequence:

- GroundRecall should support parallel workers and later consolidation
- coordinator and merge logic should not depend on learner-session code

## Boundary Rules

### Put functionality in Didactopus when:

- the capability is inherently learner-facing
- the output is a study path, mentor turn, practice task, or mastery-oriented review
- the value depends on pedagogy

### Put functionality in GroundRecall when:

- the capability is useful with no learner present
- the artifact is canonical knowledge rather than curriculum UX
- the feature concerns ingestion, promotion, query, export, sync, or merge
- the result should be shared across Codex, Claude Code, or future assistants

### Put functionality in GenieHive when:

- the question is which model, service, or route should handle a request
- the feature concerns health, availability, route resolution, or cluster inspection

## CLI Direction

### Short term

- allow a modest umbrella CLI inside `didactopus`
- keep `provider-inspect` available there because it is already useful operationally
- continue using repo-local modules while boundaries are still stabilizing

### Medium term

- maintain separate operator surfaces:
  - `didactopus` for learner and review workflows
  - `groundrecall` for knowledge-substrate operations
  - `geniehive` for routing and cluster inspection

### Long term

- treat Didactopus as one client of GroundRecall, not the owner of all GroundRecall operations
- keep assistant-neutral knowledge functions deployable without Didactopus

## Migration Guidance From The Current Repo

The current repository already contains GroundRecall code under `src/didactopus/`. That is acceptable as an implementation phase, but the intended product boundary is clearer than the current package boundary.

Recommended migration sequence:

1. Keep new learner-facing flows in Didactopus.
2. Keep new knowledge-substrate semantics in GroundRecall-oriented modules.
3. Avoid adding generic sync/merge/query/export operations only to `didactopus.main`.
4. Promote GroundRecall commands toward an explicit CLI namespace once sync and merge mature.
5. Keep GenieHive inspection/routing logic out of learner-specific modules except through narrow policy helpers.

## Immediate Planning Consequence

When evaluating a new feature, first ask:

1. Is this useful without a learner?
2. Is this useful without a curriculum pack?
3. Is this about canonical knowledge state or educational interaction?
4. Would teams need this even if they never run Didactopus UI?

If the answers point away from pedagogy, prefer GroundRecall as the long-term home.
