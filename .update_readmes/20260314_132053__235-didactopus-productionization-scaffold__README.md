# Didactopus Productionization Scaffold

This update takes the prior authenticated API/database prototype one step closer to a
production-ready shape.

## Added in this scaffold

- PostgreSQL-first configuration
- JWT-style auth scaffold with access/refresh token concepts
- role-based authorization model
- background worker queue scaffold
- evaluator history endpoints
- learner-management endpoints
- pack-administration endpoints
- Docker Compose layout for API + worker + PostgreSQL

## Important note

This is still a scaffold, not a hardened deployment:
- JWT signing secrets are placeholder-driven
- queue processing is still simplified
- no TLS termination is included here
- migrations are not fully implemented

## Intended next steps

- replace placeholders with deployment secrets
- add Alembic migrations
- add Redis-backed queue or a more robust worker setup
- connect the learner UI to the new admin/evaluator-history endpoints
