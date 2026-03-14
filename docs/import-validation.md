# Import Validation and Safety

The import validation layer sits between generated draft packs and managed
review workspaces.

## Why it exists

Importing should not be a blind file copy. Users need to know whether a draft
pack appears structurally usable before it is brought into a workspace.

## Current checks

The scaffold validates:
- presence of required files
- parseability of `pack.yaml`
- parseability of `concepts.yaml`
- basic pack metadata fields
- concept count
- overwrite risk for target workspace

## Current outputs

The preview step returns:
- `ok`
- blocking errors
- warnings
- pack summary
- overwrite warning
- import readiness flag

## Future work

- stronger schema validation
- version compatibility checks against Didactopus core
- validation of roadmap/projects/rubrics coherence
- file diff preview when overwriting
- conflict-aware import merge rather than replacement copy
