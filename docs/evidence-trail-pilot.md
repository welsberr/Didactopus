# Evidence Trail Pilot

This note records the repository-owned learner-workbench example built around
question framing, source comparison, bibliography growth, and reflective
revision.

## Repository artifacts

The pack and its learner-facing projection live in:

- `domain-packs/evidence-trail/`
- `webui/public/packs/evidence-trail-pack.json`

The source URLs in `pack_compliance_manifest.json` are retained as provenance.
They are not fetched by the learner workbench and do not define a runtime or
deployment dependency.

## Learner-workbench role

The example should demonstrate a portable flow:

1. load a compatible pack;
2. show onboarding and the current concept path;
3. ask for a grounded learner response;
4. keep observation and interpretation distinct;
5. return evaluator feedback and a next study action.

Any website, course repository, or local pack library may link to or embed the
workbench. Deployment-specific links and publication commands belong to that
producer, not to Didactopus.
