# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform designed to help motivated learners achieve genuine mastery through Socratic mentoring, structured practice, project work, verification, and competency-based evaluation.

**Tagline:** *Many arms, one goal — mastery.*

## Vision

Didactopus treats AI as a **mentor, curriculum planner, critic, evaluator, and project guide** rather than an answer vending machine. The design goal is to produce capable practitioners who can explain, apply, test, and extend knowledge in real settings.

The platform is meant to support **AI-assisted autodidacts**: learners who pursue real expertise outside, alongside, or beyond traditional institutions.

## Core principles

- Active learning over passive consumption
- Socratic questioning over direct answer dumping
- Verification culture over uncritical acceptance
- Competency gates over time-based progression
- Project-based evidence of mastery
- Local-first model use when available
- Portable, shareable domain plans and learning artifacts

## Initial architecture

The initial prototype is organized around six core services:

1. **Domain Mapping Engine**  
   Builds a concept graph for a target field, including prerequisites, competencies, canonical problem types, and artifact templates.

2. **Curriculum Generator**  
   Produces a staged learning roadmap adapted to learner goals and prior knowledge.

3. **Mentor Agent**  
   Conducts Socratic dialogue, reviews reasoning, and offers targeted critique.

4. **Practice Generator**  
   Produces exercises aimed at specific concepts and skill gaps.

5. **Project Advisor**  
   Proposes and scaffolds real projects that demonstrate competence.

6. **Evaluation System**  
   Scores explanations, problem solutions, project outputs, and transfer tasks against explicit rubrics.

## Distribution model for contributed learning content

Didactopus is designed to support distribution of contributed artifacts, including:

- domain plans
- concept maps
- curriculum templates
- exercise sets
- project blueprints
- evaluation rubrics
- benchmark packs
- exemplar portfolios

These should be shareable as versioned packages or repositories so that contributors can publish reusable mastery paths for particular domains.

See:
- `docs/artifact-distribution.md`
- `docs/domain-pack-format.md`

## Local model strategy

The codebase is designed to support a provider abstraction:

- **Local-first**: Ollama, llama.cpp server, vLLM, LM Studio, or other on-prem inference endpoints
- **Remote optional**: API-backed models only when configured
- **Hybrid mode**: local models for routine mentoring, remote models only for heavier synthesis or evaluation if explicitly allowed

## Repository layout

```text
didactopus/
├── README.md
├── LICENSE
├── pyproject.toml
├── Makefile
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── .github/workflows/ci.yml
├── configs/
│   └── config.example.yaml
├── docs/
│   ├── architecture.md
│   ├── repository-plan.md
│   ├── component-specs.md
│   ├── prototype-roadmap.md
│   ├── artifact-distribution.md
│   └── domain-pack-format.md
├── domain-packs/
│   └── example-statistics/
│       ├── pack.yaml
│       ├── concepts.yaml
│       ├── roadmap.yaml
│       ├── projects.yaml
│       └── rubrics.yaml
├── src/didactopus/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── model_provider.py
│   ├── domain_map.py
│   ├── curriculum.py
│   ├── mentor.py
│   ├── practice.py
│   ├── project_advisor.py
│   ├── evaluation.py
│   └── artifact_registry.py
└── tests/
    ├── test_config.py
    ├── test_domain_map.py
    └── test_artifact_registry.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp configs/config.example.yaml configs/config.yaml
python -m didactopus.main --domain "statistics" --goal "reach practical mastery"
pytest
```

## Prototype capabilities in this scaffold

The current scaffold provides:

- a configuration model for local/remote provider selection
- a concept graph data structure for domain maps
- stubs for curriculum, mentor, practice, project, and evaluation services
- a simple artifact registry for local domain-pack discovery
- an example domain pack layout
- a CLI entry point to demonstrate end-to-end flow
- tests to validate configuration and artifact behavior

## Suggested first implementation milestones

### Milestone 1: Learner and domain modeling
- learner profile schema
- concept graph generation
- prerequisite traversal
- domain-pack schema validation
- local artifact discovery

### Milestone 2: Guided study loop
- Socratic mentor prompts
- explanation checking
- exercise generation by competency target
- evidence capture for learner work

### Milestone 3: Project-centered learning
- capstone generator
- milestone planning
- artifact review rubrics
- distributed project pack ingestion

### Milestone 4: Mastery evidence
- explanation scoring
- transfer tasks
- benchmark alignment
- progress dashboard
- artifact publication workflow

## Notes on evaluation design

A key design choice is that the assessment layer should look for:

- correct explanations in the learner's own words
- ability to solve novel problems
- detection of flawed reasoning
- evidence of successful project execution
- transfer across adjacent contexts

## Naming rationale

**Didactopus** combines *didactic* / *didact* with *octopus*: a central intelligence coordinating many arms of learning support.

## License

MIT
