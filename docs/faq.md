# FAQ

## What is Didactopus, in one sentence?

Didactopus turns educational material into structured learning packs, then uses graphs, evidence, and review workflows to support human or AI learning against those packs.

## Is this meant to help me learn, or to do the work for me?

It is meant to help you learn.

The intended role is:

- clarify topic structure
- surface prerequisites
- suggest study order
- provide explanations, comparisons, and self-checks
- help you see where your understanding is weak

The intended role is not:

- silently complete coursework for you
- replace the need to explain ideas in your own words
- turn learning into answer copying

In other words, Didactopus is supposed to reduce confusion and friction without encouraging the offloading effect of unstructured GenAI use.

## Is this a packaged application or a research/workbench repository?

It is a workbench-style repository with runnable code, tests, example packs, generated outputs, and local-first review/demo flows.

## I am one person trying to learn a topic. What is the fastest useful way to use this?

Use the included MIT OCW Information and Entropy demo first.

Run:

```bash
pip install -e .
python -m didactopus.ocw_information_entropy_demo
python -m didactopus.ocw_progress_viz
python -m didactopus.ocw_skill_agent_demo
```

That gives you, with minimal setup:

- a generated topic pack
- a guided curriculum path
- a learner progress view
- a capability export
- a reusable skill bundle
- a demo of an agentic system using that skill

If you only want to see whether Didactopus feels useful as a personal mentor scaffold, this is the right place to start.

## What is the fastest custom route for a single learner?

Start from one Markdown or text file for a topic you care about.

The lightest custom pattern is:

1. Prepare a single source file with lesson headings, short descriptions, objectives, and exercises.
2. Use the OCW demo source in `examples/ocw-information-entropy/` as the model.
3. Adapt the same pipeline shape used by `didactopus.ocw_information_entropy_demo`.
4. Review the resulting draft pack just enough to remove obvious noise.

The current system is best when used as "generate a usable map quickly, then refine only what matters."

## What is a domain pack?

A domain pack is the unit Didactopus uses to represent a learning domain. In practice it is a directory containing:

- `pack.yaml`
- `concepts.yaml`
- `roadmap.yaml`
- `projects.yaml`
- `rubrics.yaml`

Generated packs may also include review, conflict, and attribution artifacts.

## What is the difference between a draft pack and a reviewed pack?

A draft pack is an ingestion output. A reviewed pack is a pack that has been loaded into the review workflow, edited or triaged by a reviewer, and exported again with review metadata applied.

## What does the workspace manager do?

It keeps review work organized. The current implementation supports:

- create workspace
- list workspaces
- touch/open recent workspaces
- preview draft-pack import
- import draft packs into `workspace/draft_pack/`
- overwrite checks before replacing an existing draft pack

## Does Didactopus really ingest PDF, DOCX, and PPTX files?

Yes, but conservatively. Those adapters currently normalize text in a simplified way. They exist to stabilize the interface and surrounding workflow rather than to claim production-grade document parsing.

## Does the agentic learner call an external LLM?

No. The current agentic learner paths are deterministic and synthetic. They are meant to exercise the orchestration pattern, evaluator pipeline, mastery updates, capability export, and visualization flow without requiring an external model service.

## Can I still use it as a personal mentor even though the learner is synthetic?

Yes, if you think of the current repo as a structured learning workbench rather than a chat product.

Right now the value is in:

- turning source material into a concept/path structure
- making prerequisites explicit
- exporting progress and capability artifacts
- generating reusable skill context for future tutoring or evaluation

The current demos show the shape of a mentor workflow even though the agent itself is not yet a live external model integration.

## How should I use it if I am taking a course and do not want to hire a tutor?

Use it as a structured study companion:

1. Build or load a topic pack.
2. Use the path and prerequisite structure to see what to study next.
3. Ask for hints, comparisons, and explanation prompts.
4. Use progress artifacts to identify gaps.
5. Do the actual solving and writing yourself.

That keeps the system on the "guided practice" side of the line instead of the "outsourced thinking" side.

## What is the current evidence model?

The evidence engine supports:

- evidence items grouped by concept
- per-type weighting
- optional recency weighting
- confidence derived from accumulated evidence mass
- dimension-level summaries
- resurfacing when recent weak evidence drags mastery below threshold

## What does the capability export contain?

The exported capability profile includes:

- learner identity
- target domain
- mastered concepts
- weak dimensions by concept
- evaluator summaries by concept
- artifact records

The main export formats are JSON, Markdown, and an artifact manifest.

## What is the MIT OCW Information and Entropy demo?

It is the repo's current end-to-end reference flow. Running:

```bash
python -m didactopus.ocw_information_entropy_demo
```

generates:

- a new pack in `domain-packs/mit-ocw-information-entropy/`
- learner outputs in `examples/ocw-information-entropy-run/`
- a repo-local skill bundle in `skills/ocw-information-entropy-agent/`
- an agentic skill-usage demo in `examples/ocw-information-entropy-skill-demo/`
- compliance artifacts including `pack_compliance_manifest.json` and `source_inventory.yaml`

## What visualizations exist today?

The OCW demo currently generates two visualization modes:

- a guided-path learner progress view
- a full concept map that also surfaces noisy non-path concepts

You can render them with:

```bash
python -m didactopus.ocw_progress_viz
python -m didactopus.ocw_progress_viz --full-map
```

## What should I expect to review manually?

Today, usually:

- noisy concept candidates from extraction
- weak or missing mastery signals
- any prerequisite ordering that feels too thin or too rigid

The fastest productive workflow is not to perfect everything. It is to prune obvious noise and keep moving.

## Is the generated content free of extractor noise?

No. The current extractors can still emit noisy candidate concepts, especially from title-cased phrases embedded in lesson text. That is why review flags, workspace review, and promotion flows are first-class parts of the project.

## How should I think about validation versus QA?

Validation is structural: required files, schemas, references, duplicates, dependencies.

QA is heuristic: coverage alignment, evaluator alignment, path quality, semantic QA, and related diagnostics that try to surface likely quality problems before or during review.

## Where should I start reading if I want the full project overview?

Start with:

- `README.md`
- `docs/course-to-pack.md`
- `docs/learning-graph.md`
- `docs/mastery-ledger.md`
- `docs/workspace-manager.md`
- `docs/interactive-review-ui.md`

## How is Didactopus made?

Didactopus started with an idea from Wesley R. Elsberry, and has been
generated through prompting and refinement via OpenAI's ChatGPT 5.4
and OpenAI Codex with GPT 5.4. It uses tests and demonstration runs
via Codex to confirm functionality, fix bugs, and update
documentation. Elsberry provided goals, direction, operational
principles, and orchestration, and generative AI has provided pretty
much the rest.
