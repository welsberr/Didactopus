# Didactopus Backend API Prototype

This update adds a small real backend API scaffold for:

- pack registry listing
- learner-state persistence outside the browser
- evaluator-result ingestion into mastery records

## What is included

### Backend
A lightweight FastAPI-style scaffold with:
- `GET /api/packs`
- `GET /api/packs/{pack_id}`
- `GET /api/learners/{learner_id}/state`
- `PUT /api/learners/{learner_id}/state`
- `POST /api/learners/{learner_id}/evidence`
- `GET /api/learners/{learner_id}/recommendations/{pack_id}`

The backend uses simple file-backed JSON storage so the prototype remains easy to inspect and modify.

### Frontend
The learner UI is updated to:
- load pack registry from the backend
- load learner state from the backend
- persist learner state through the backend
- submit simulated evidence events to the backend
- render recommendations returned by the backend

## Why this matters

This is the first step from a single-browser prototype toward a genuinely multi-session, multi-user system:
- learner state no longer has to live only in local storage
- recommendations can be centralized
- evaluator output can enter the same evidence pathway as UI-generated events
- future real evaluators can update learner state without changing the learner UI architecture

## Prototype scope

This remains intentionally small:
- file-backed storage
- no authentication yet
- no database dependency yet
- simulated evaluator/evidence flow still simple

That makes it appropriate for rapid iteration while preserving a clean path to later migration.
