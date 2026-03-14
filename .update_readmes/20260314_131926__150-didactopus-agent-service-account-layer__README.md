# Didactopus Agent Service Account Layer

This update extends the deployment-policy and agent-hooks scaffold with a
**first-class service-account model for AI learners and other non-human agents**.

## Added in this scaffold

- service-account records
- scoped API tokens for agents
- capability scopes for learner workflows
- direct agent authentication endpoint
- scope checks for agent operations
- admin UI for viewing service accounts and their scopes

## Why this matters

An AI learner should not need to masquerade as a human user session.

With this layer, an installation can:
- create a dedicated machine identity
- give it only the scopes it needs
- allow it to operate through the same API surfaces as the UI
- keep agent permissions narrower than full admin access when appropriate

## Example scopes

- `packs:read`
- `packs:write_personal`
- `contributions:submit`
- `learners:read`
- `learners:write`
- `recommendations:read`
- `evaluators:submit`
- `evaluators:read`
- `governance:read`
- `governance:write`

## Strong next step

- key rotation and revocation UI
- service-account ownership and audit trails
- structured workflow schema export for agents
- explicit agent-run logs tied to service-account identity
