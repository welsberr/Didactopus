# Didactopus Auth + DB + Async Evaluator Prototype

This update extends the backend API prototype with scaffolding for:

- authentication and multi-user separation
- a real database backend (SQLite via SQLAlchemy)
- evaluator job submission
- asynchronous result ingestion into learner mastery records

## What is included

### Authentication and user separation
This prototype introduces:
- user records
- simple token-based auth scaffold
- learner-state ownership checks
- per-user learner records

This is intentionally minimal and suitable for local development, not production hardening.

### Database backend
The file-backed JSON store is replaced here with a relational persistence scaffold:
- SQLite database by default
- SQLAlchemy ORM models
- tables for users, packs, learners, mastery records, evidence events, evaluator jobs

### Async evaluator jobs
This prototype adds:
- evaluator job submission endpoint
- background worker scaffold
- evaluator results persisted to the database
- resulting evidence events applied into learner mastery records

## Why this matters

This is the first version that structurally supports:
- multiple users
- persistent learner history in a real database
- evaluator-driven evidence arriving later than the UI request that triggered it

That is the correct shape for turning Didactopus into a genuine multi-user learning platform.

## Important note

This remains a prototype scaffold:
- auth is deliberately simple
- SQLite is used for ease of inspection
- background job execution uses FastAPI background tasks rather than a production queue
- secrets, password hardening, and deployment concerns still need a later pass

## Next likely step

- replace simple token auth with stronger session/JWT handling
- migrate from SQLite to PostgreSQL
- add role-based authorization
- move evaluator jobs to a real queue such as Celery/RQ/Arq
- expose evaluator traces and job history in the learner UI
