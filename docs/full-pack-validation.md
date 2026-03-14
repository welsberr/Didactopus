# Full Pack Validation

The full pack validator inspects the main Didactopus pack artifacts together.

## Purpose

Basic file checks are not enough. A pack can parse successfully while still being
internally inconsistent.

## Files checked

- `pack.yaml`
- `concepts.yaml`
- `roadmap.yaml`
- `projects.yaml`
- `rubrics.yaml`

## Current validation categories

### File and parse checks
- required files present
- YAML parseable

### Pack metadata checks
- `name`
- `display_name`
- `version`

### Concept checks
- concept list exists
- duplicate concept ids
- missing titles
- missing or very thin descriptions

### Roadmap checks
- stage list exists
- stage concepts refer to known concepts

### Project checks
- project list exists
- project prerequisite concepts refer to known concepts

### Rubric checks
- rubric list exists
- each rubric has `id`
- rubric has at least one criterion when present

## Output

Validation returns:
- blocking errors
- warnings
- structured summary counts
- import readiness

## Future work

- cross-pack dependency validation
- mastery-profile validation
- stronger rubric schema
- semantic duplicate detection
- prerequisite cycle detection
- version compatibility checks
