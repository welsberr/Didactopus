# Didactopus Dual-Lane Policy Layer

This update extends the contribution-management scaffold with a **dual-lane policy model**:

- a **personal lane** for individuals building domain packs for their own use
- a **community lane** for contributed packs that enter shared review and publication workflows

## Design intent

A single user working privately with Didactopus should **not** be blocked by governance overhead
when constructing packs for their own purposes.

At the same time, community-shared packs should still be subject to:
- contribution intake
- validation and provenance gates
- reviewer workflows
- approval before publication

## Added in this scaffold

- pack policy lane metadata (`personal`, `community`)
- bypass rules for personal packs
- community-only gate enforcement for publication workflows
- UI distinction between personal-authoring and community-submission flows
- reviewer-assignment and approval-policy scaffolding for community packs only

## Resulting behavior

### Personal lane
A user can:
- create and revise packs directly
- publish locally for their own use
- bypass reviewer task queues
- inspect validation/provenance without being blocked by them

### Community lane
A contributor can:
- submit a pack or revision for review
- see gate summaries and diffs
- enter reviewer assignment and approval workflow
- require policy satisfaction before publish

## Strong next step

- per-installation policy settings
- optional stricter local policies for teams or labs
- semantic diffing and structured reviewer checklists
