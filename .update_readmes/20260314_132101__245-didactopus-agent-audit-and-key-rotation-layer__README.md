# Didactopus Agent Audit Logging + Key Rotation Layer

This update extends the service-account scaffold with two operational controls:

- **audit logging** for machine-initiated activity
- **key rotation / revocation scaffolding** for service accounts

## Added in this scaffold

- audit log records for service-account actions
- request-level audit helper for agent operations
- service-account secret rotation endpoint
- service-account enable/disable endpoint
- admin UI for viewing audit events and rotating credentials

## Why this matters

A serious AI learner deployment needs more than scoped credentials.

It also needs to answer:

- which service account did what?
- when did it do it?
- what endpoint or workflow did it invoke?
- can we replace or revoke a compromised credential?

This layer makes service-account usage more accountable and more maintainable.
