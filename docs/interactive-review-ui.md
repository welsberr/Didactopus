# Interactive Review UI

This revision introduces a React-based local SPA for reviewing draft packs.

## Goals

- reduce curation friction
- make review decisions explicit
- allow pack promotion after inspection
- preserve provenance and review rationale

## Features in this scaffold

- concept list with editable fields
- trust status editing
- concept notes editing
- prerequisite editing
- conflict visibility and resolution
- promoted-pack export generation in-browser logic

## Data model

The SPA loads `review_data.json` and can emit:
- updated review state
- review ledger entries
- promoted concepts payload

## Next steps

- file open/save integration
- conflict filtering
- merge/split concept actions in UI
- richer diff views
- domain-pack validation from the UI
