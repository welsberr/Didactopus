# Didactopus

**Didactopus** is a local-first AI-assisted autodidactic mastery platform designed to help motivated learners achieve genuine mastery through Socratic mentoring, structured practice, project work, verification, and competency-based evaluation.

**Tagline:** *Many arms, one goal — mastery.*

## This revision adds

- dependency and compatibility checks for domain packs
- version-range validation against the Didactopus core version
- local dependency resolution across installed packs
- richer pack manifests
- repository artwork under `artwork/`
- tests for dependency and compatibility behavior

## Domain packs

Didactopus supports portable, versioned **domain packs** that can contain:

- concept maps
- roadmap templates
- project blueprints
- rubrics
- benchmark tasks
- resource guides

Packs can depend on other packs, enabling layered curricula and reusable foundations.

## Artwork

The repository includes whimsical project art at:

- `artwork/didactopus-mascot.png`

Suggested future additions:
- `artwork/didactopus-banner.png`
- `artwork/didactopus-logo.png`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m didactopus.main --domain "statistics" --goal "practical mastery"
pytest
```
