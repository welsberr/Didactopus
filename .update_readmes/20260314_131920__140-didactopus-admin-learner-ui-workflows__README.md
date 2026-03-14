# Didactopus Admin + Learner UI Workflows

This update builds the next layer on top of the productionization scaffold by wiring
the frontend toward real workflow surfaces:

- login with token storage
- token refresh handling
- learner dashboard flow
- evaluator-history view
- learner-management view
- admin pack creation / publication view

## Included

### Frontend
- login screen
- auth context with token refresh scaffold
- learner dashboard
- evaluator history panel
- learner management panel
- admin pack editor / publisher panel
- shared API client

### Backend additions
- learner listing endpoint
- admin pack listing endpoint
- admin pack publication toggle endpoint

## Scope
This remains a scaffold intended to connect the architectural pieces and establish
usable interaction flows. It is not yet a polished production UI.

## Intended next step
- integrate richer form validation
- add pack schema editing tools
- connect evaluator traces and rubric results
- add paginated audit history
