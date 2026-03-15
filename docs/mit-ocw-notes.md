# MIT OpenCourseWare Notes

MIT OpenCourseWare material is a good fit for Didactopus demos, but it needs explicit attribution and license handling.

## Current handling in this repository

The MIT OCW Information and Entropy demo stores:

- a local derived source file in `examples/ocw-information-entropy/`
- a `sources.yaml` source inventory beside that file
- attribution and rights notes in the generated pack
- a generated `pack_compliance_manifest.json` in the generated pack
- generated learner outputs in `examples/ocw-information-entropy-run/`
- a repo-local skill bundle in `skills/ocw-information-entropy-agent/`

## License handling stance

MIT OpenCourseWare course content is generally distributed under CC BY-NC-SA 4.0, with the important caveat that linked or third-party materials may not always be covered.

That means Didactopus should:

- preserve MIT OCW attribution
- keep a rights note in generated artifacts
- treat redistributable derived packs as reviewable outputs rather than unquestioned mirrors
- preserve noncommercial and share-alike implications when applicable

## Practical guidance

When building from MIT OCW sources:

- record the course page and any unit/resource pages used
- keep those records in a per-course `sources.yaml` inventory
- separate core MIT OCW material from excluded third-party items if they appear
- keep generated pack content clearly marked as adapted/derived
- include attribution and compliance artifacts with the emitted pack

For the full workflow, see `docs/mit-ocw-course-guide.md`.
