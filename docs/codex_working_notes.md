# Codex working notes for Didactopustry1

## Priority
Stabilize public API compatibility before adding new features.

## Compatibility policy
Older test-facing public names should remain importable even if implemented as wrappers.

## Python version
Assume Python 3.10 compatibility.

## Preferred workflow
1. Read failing tests.
2. Patch the smallest number of files.
3. Run targeted pytest modules.
4. Run full pytest.
5. Summarize by subsystem.

## Avoid
- broad renames
- deleting newer architecture
- refactors unrelated to failing tests

