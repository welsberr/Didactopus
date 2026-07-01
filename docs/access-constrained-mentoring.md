# Access-Constrained Mentoring Roadmap

Didactopus should eventually support mentoring in places where ordinary access
to education is limited by poverty, geography, disability, social exclusion, or
hostile authorities. This is a human-rights and personal-security concern, but
the project should be careful about its claims: Didactopus can reduce
dependence on privileged human tutors and network services; it cannot guarantee
personal safety, anonymity, or legal protection.

The design target is an offline-first, source-grounded mentoring system that a
local steward can operate with modest technical skill and that a learner can use
without needing cloud accounts, remote tutors, or continuous internet access.

## Design Principles

- Treat access-constrained education as a first-class deployment mode.
- Prefer local inference and local retrieval before remote services.
- Ship useful reviewed learning packs, not only tooling for experts.
- Make setup, health checks, updates, and backups understandable to a
  non-specialist steward.
- Minimize collection of learner identity and sensitive context.
- Keep telemetry off by default; remote connections must be explicit.
- Preserve provenance and source-grounding even in offline mode.
- Separate human learner records, AI learner benchmark records, and operator
  maintenance records.
- Avoid claims of secrecy or protection from state-level adversaries.
- Require local legal, social, and personal-risk assessment before high-risk
  deployments.

## Deployment Target

The primary product shape is an access-constrained learner appliance:

- Didactopus learner interface;
- curated learning packs;
- GroundRecall-backed source, concept, and provenance store;
- local search and retrieval indexes;
- local LLM route through GenieHive, Ollama, llama.cpp, or another self-hosted
  backend;
- local-only learner ledger by default;
- optional steward dashboard for updates, health checks, and pack management.

It should support several profiles:

- single-learner laptop;
- family or shared-device learner station;
- small LAN classroom or study circle;
- offline library or community kiosk;
- removable-media pack review and update station.

## Learner Safety And Privacy Requirements

The default system should:

- avoid requiring real names, demographics, political affiliation, or location;
- allow pseudonymous or local-only learner profiles;
- keep learner work and mastery records on the local device unless deliberately
  exported;
- make data export, archive, and deletion clear to a local steward;
- avoid analytics, cloud sync, crash upload, and automatic external calls unless
  explicitly configured;
- label remote model routes and external retrieval clearly before use;
- keep restricted Library material and unreviewed draft records out of
  learner-facing public exports.

Security-sensitive deployments need separate review by people who understand
the local threat model. Didactopus documentation should not imply that ordinary
application settings are enough for every hostile environment.

## Reducing Operator Privilege Requirements

The long-term goal is not to require a sophisticated technologist for every
learner. The system should move from "expert operator" toward "local steward":

- installer profiles with plain-language choices;
- preflight checks for model availability, disk, GPU/CPU, pack integrity, and
  offline mode;
- status pages that distinguish "ready for learning" from "needs maintenance";
- signed release bundles and pack checksums;
- printable steward guides;
- recovery procedures for corrupted indexes, missing models, and failed
  updates;
- pack installation that does not require editing configuration files.

The steward should not need to understand Docker, Python packaging, LLM context
windows, vector search internals, or Git to keep a basic learner node operating.

## Curriculum And Pack Requirements

Access-constrained deployments need packs that are immediately useful:

- literacy, numeracy, science, math, language learning, health, and practical
  reasoning foundations;
- modular topic packs that can be installed without the whole Library;
- source spines, worked examples, faded examples, retrieval practice, answer
  keys, and remediation paths;
- accessible HTML/text output and printable study sheets;
- localizable examples and glossary records;
- clear license and redistribution metadata;
- reviewed coverage ledgers that say what the pack does and does not teach.

The pack format should support low-bandwidth distribution through removable
media or local mirrors. Signed packs and checksums are important because
learners and stewards may not be able to verify provenance online.

The stack should use external standards as adapters where they reduce friction:
Common Cartridge for LMS exchange, QTI for assessment items, EPUB and ZIM/static
bundles for offline reading and libraries, H5P metadata for interactive assets,
and optional xAPI only for local learner-event interchange. The detailed plan is
in [interoperability-and-feature-adoption.md](interoperability-and-feature-adoption.md).

## Mentoring Requirements

The mentor loop should work when no human tutor is available:

- source-blind initial assessment;
- source-spine orientation;
- learner attempt before answer;
- worked example or contrast case;
- faded practice;
- feedback that names the failed distinction;
- confidence calibration and abstention practice;
- retention checks after context reset;
- remediation path when the learner is stuck.

For local LLMs, model adequacy must be tested per pack and per role. A model
that is acceptable for retrieval-grounded hinting may not be acceptable as an
evaluator. A smaller model may be useful for practice generation but not for
high-stakes feedback.

## Roadmap

### Phase 1. Policy And Architecture Baseline

- Document access-constrained mentoring as a deployment mode.
- Define privacy, telemetry, local-only, and remote-route policies.
- Add threat-model notes without promising secrecy.
- Identify which capabilities belong in Didactopus, GroundRecall, and
  GenieHive.

### Phase 2. Offline Learner Appliance Prototype

- Package Didactopus, GroundRecall, local search, and one local model route into
  a repeatable single-machine profile.
- Add a setup health check and a "ready for learning" status report.
- Provide an offline demo pack with no network dependency.
- Confirm that normal learner sessions do not require external calls.

### Phase 3. Pack Capsules And Distribution

- Define a pack capsule manifest with content, license, checksums, model
  requirements, language, accessibility features, and review status.
- Support import from local directory, archive file, or removable media.
- Add signed-pack verification when signing infrastructure is available.
- Generate printable steward and learner guides from pack metadata.
- Add boundary adapters for Common Cartridge, QTI, EPUB, ZIM/static bundles, and
  H5P metadata after the pack capsule manifest is stable.

### Phase 4. Steward Experience

- Build a low-expertise steward dashboard or CLI wrapper.
- Add plain-language diagnostics and recovery steps.
- Provide update, backup, export, and deletion workflows.
- Keep advanced configuration available but out of the ordinary path.

### Phase 5. Local Model Adequacy Matrix

- Benchmark small, medium, and stronger local models by role and pack.
- Track accuracy, calibration, abstention, hallucination, latency, and memory.
- Publish deployment profiles for CPU-only, small GPU, laptop GPU, and stronger
  local hosts.
- Require pack-level model warnings when a route is below adequacy thresholds.

### Phase 6. Accessibility And Localization

- Make text-first and screen-reader-friendly learner flows the baseline.
- Add local TTS/STT only after text accessibility is solid.
- Support translated packs with visible translation status and review level.
- Let communities substitute local examples while preserving source grounding.

### Phase 7. Human Pilot And Field Readiness

- Pilot in low-risk settings before any high-risk deployment.
- Measure learning with pretest, posttest, retention, and calibration.
- Collect steward-maintenance friction separately from learner outcomes.
- Establish red-team review for privacy, data retention, and unsafe model
  behavior.

## Non-Goals And Red Lines

- Do not present Didactopus as a tool for evading law enforcement or defeating
  surveillance.
- Do not add hidden telemetry, learner tracking, or covert remote management.
- Do not require cloud accounts for the basic learner path.
- Do not certify learning solely from conversational fluency.
- Do not expose restricted or unreviewed Library material through public learner
  exports.
- Do not deploy high-risk content or learner records without local human-rights,
  legal, and safety review.
