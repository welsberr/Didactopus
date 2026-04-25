# evo-edu Evidence Trail Pilot

This note captures the first concrete integration path between `evo-edu.org`
and Didactopus.

## Why this pack first

`Evidence Trail` is the best first pilot because it already matches the
strongest current Didactopus behaviors:

- question framing
- source-grounded study
- concept sequencing
- reflective revision
- bibliography growth

It is a better fit for the first learner-workbench pilot than a more
model-heavy pack such as `Population Change`.

## Current repo artifacts

This pilot now has a first pack skeleton in:

- `domain-packs/evidence-trail/pack.yaml`
- `domain-packs/evidence-trail/concepts.yaml`
- `domain-packs/evidence-trail/pack_compliance_manifest.json`
- `domain-packs/evidence-trail/pack.frontend.json`

and a learner-facing frontend payload copy in:

- `webui/public/packs/evidence-trail-pack.json`

## Immediate next UI step

The current `webui/` is still review-workbench-first. The next useful step is
to add a learner-workbench path that can load `evidence-trail-pack.json` and
show:

- onboarding headline/body/checklist
- current concept
- prerequisite path
- one grounded prompt
- learner response
- evaluator feedback
- next study action

## Integration back to evo-edu.org

Once a learner-workbench route exists, `evo-edu.org` should link to it from:

- `/evo/packs/evidence-trail/`
- `/evo/packs/evidence-trail/study-log.html`
- `/evo/pathways/self-learners/`

The framing should remain:

- guided-study workbench
- source-grounded reflection companion

not generic AI tutor.
