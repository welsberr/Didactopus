# Didactopus Deployment Policy + Agent Hooks Layer

This update extends the dual-lane policy scaffold with two related concerns:

1. **Deployment policy settings**
   - single-user / private-first
   - team / lab
   - community repository

2. **AI learner / agent hook parity**
   - explicit API surfaces for agentic learners
   - capability discovery endpoints
   - task-oriented endpoints parallel to the UI workflows
   - access to pack, learner, evaluator, and recommendation workflows without relying on the UI

## Why this matters

Didactopus should remain usable in two modes:

- a human using the UI directly
- an AI learner or agentic orchestrator using the API directly

The AI learner should not lose capability simply because a human-facing UI exists.
Instead, the UI should be understood as a thin client over API functionality.

## What is added

- deployment policy profile model and endpoint
- policy-aware defaults for pack lane behavior
- agent capability manifest endpoint
- agent learner workflow endpoints
- explicit notes documenting API parity with UI workflows

## AI learner capability check

This scaffold makes the AI-learner situation clearer:

- yes, the API still exposes the essential learner operations
- yes, pack access, recommendations, evaluator job submission, and learner-state access remain directly callable
- yes, there is now an explicit capability-discovery endpoint so an agent can inspect what the installation supports

## Strong next step

- add service-account / non-human agent credentials
- formalize machine-usable schemas for workflows and actions
- add structured action planning endpoint for agentic learners
