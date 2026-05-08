# Foundation Notebook Inception Pilot

This note turns the broader Notebook pipeline into one concrete first run.

It answers a narrower question than
[evo-edu-notebook-pipeline.md](./evo-edu-notebook-pipeline.md):

- what is the first pilot region,
- what repos and commands are already ready,
- what exact artifacts should be produced,
- and what still blocks calling the Notebook "incepted".

## Current status

The stack is already past pure planning.

Implemented now:

- `CiteGeist` can export Notebook-ready topic bibliography bundles with
  `export-notebook-topic`.
- `GroundRecall` can export `groundrecall_query_bundle.json` for one concept.
- `Didactopus` can build `notebook_page.json` directly from a GroundRecall
  concept or bundle.
- `Didactopus` pack emission can already carry Notebook-facing artifacts.

Not yet done:

- one named pilot source workspace
- one reviewed pilot concept region carried end to end on real local sources
- one first published Notebook page candidate built from those real sources

So the missing step is no longer "invent Notebook machinery". The missing step
is "run one reproducible pilot from provisioned local sources".

## Chosen first pilot

Use:

- `natural selection and adaptation`

Reasons:

- it is already represented in the Notebook page tests and example graph
  structure:
  - `natural-selection`
  - `variation`
  - `adaptation`
  - `common descent`
- it is narrow enough for a first pass
- it is central enough that the Notebook navigation model is meaningful
- it can draw on both textbook and web-corpus sources without needing an
  enormous bibliography first

This is a better first region than a broad "history of evolutionary thought"
pilot because it stresses concept navigation without forcing huge historical
scope immediately.

## Pilot revision from execution

The original pilot choice was good enough to start, but the actual run showed
that the stable Notebook center should be broader than a narrow topic label.

In practice, the pilot worked better after shifting toward a hub such as:

- `Evolutionary Dynamics of Populations`

The operational lesson is:

- narrow topics are still useful as first-ring and second-ring nodes
- but the primary Notebook page works better when anchored on a broad
  explanatory hub
- bibliography topics alone are too thin to serve as the main Notebook center

This should inform future Notebook inception work. Start with a manageable
region, but expect the durable center to be a broad explanatory hub rather than
the narrow starting label.

## Pilot workspace

Create one stable workspace outside the library root, for example:

```text
/mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/
```

Recommended layout:

```text
natural-selection/
  README.md
  manifests/
    source-manifest.yaml
  sources/
    textbooks/
    web/
    bibliographies/
  normalized/
    doclift/
  citegeist/
  groundrecall/
  didactopus/
  publish/
```

This keeps the library as upstream source storage while making the Notebook run
reproducible in one project-local tree.

## Minimum pilot sources

Start with a deliberately small set.

### Textbook side

Choose 1 to 2 textbook sections on natural selection/adaptation from the local
library root:

- `/mnt/CIFS/pengolodh/Docs/Library`

The exact textbooks can be finalized during provisioning, but the likely first
choices from the existing plan are:

- Futuyma, `Evolutionary Biology`
- Pianka, `Evolutionary Ecology`

### Web corpus side

Provision one small local snapshot from an evolution-focused corpus such as:

- TalkOrigins Archive
- Panda's Thumb

For inception, prefer a small curated subset over a full corpus mirror.

### Bibliography seed side

Use:

- one local `.bib` seed if available
- bibliography material extracted from the chosen textbook sections
- any relevant TalkOrigins bibliography fragments

## Inception steps

### Step 0. Provision the workspace

Deliverables:

- `sources/textbooks/`
- `sources/web/`
- `sources/bibliographies/`
- `manifests/source-manifest.yaml`

Completion check:

- every pilot input is copied or symlinked into the workspace
- the manifest names source type, origin, and local path

### Step 1. Normalize textbook/web material

Use `doclift` for textbook-like source material where it helps.

Expected output root:

```text
normalized/doclift/
```

Representative command pattern:

```bash
cd /home/netuser/bin/doclift
PYTHONPATH=src .venv/bin/python -m doclift.cli convert-dir \
  /path/to/pilot-source-dir \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/normalized/doclift
```

Completion check:

- a deterministic normalized bundle exists
- markdown and sidecars are present where applicable

### Step 2. Build the bibliography substrate

Use `CiteGeist` for the Notebook bibliography layer.

Representative command pattern:

```bash
cd /home/netuser/bin/CiteGeist
PYTHONPATH=src .venv/bin/python -m citegeist --db \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/citegeist/library.sqlite3 \
  ingest /path/to/pilot.bib
```

Then export the Notebook topic bibliography bundle once the pilot topic exists:

```bash
cd /home/netuser/bin/CiteGeist
PYTHONPATH=src .venv/bin/python -m citegeist --db \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/citegeist/library.sqlite3 \
  export-notebook-topic natural-selection --output-dir \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/citegeist/notebook-bundle
```

Completion check:

- `notebook_topic_bundle.json`
- `notebook_topic_bibliography.bib`

### Step 3. Import and review canonical concepts in GroundRecall

The first real review target should be the concept neighborhood around
`natural-selection`.

Expected output root:

```text
groundrecall/store/
```

Completion check:

- reviewed concept for `natural-selection`
- at least a small connected concept neighborhood
- supporting observations and source artifacts retained

### Step 4. Export the Notebook concept bundle

Use `GroundRecall` export:

```bash
PYTHONPATH=/home/netuser/bin/GroundRecall/src python -m groundrecall.export \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/groundrecall/store \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/groundrecall/export \
  --pack-ready-concept natural-selection
```

Completion check:

- `groundrecall_query_bundle.json`

### Step 5. Build the Notebook page artifact

Use the direct `Didactopus` wrapper:

```bash
didactopus notebook-page-groundrecall \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/groundrecall/store \
  natural-selection \
  /mnt/CIFS/pengolodh/Docs/Projects/evo-edu-notebook-pilot/natural-selection/didactopus/notebook-page
```

Completion check:

- `groundrecall_query_bundle.json`
- `notebook_page.json`

The page artifact should already include:

- concept summary
- graph navigation buckets
- supporting sources
- supporting excerpts
- review context
- illustration opportunities
- suggested next actions

### Step 6. Decide whether inception is complete

For this first pilot, Foundation Notebook inception should mean:

1. one stable pilot workspace exists
2. one real pilot concept region is provisioned locally
3. one reviewed `GroundRecall` concept neighborhood exists
4. one `groundrecall_query_bundle.json` exists for that concept
5. one `notebook_page.json` exists from real reviewed sources
6. one Notebook bibliography bundle exists for the same region

If all six are true, Notebook inception has happened even if public publishing
and richer UI are still pending.

## Additional lesson from the pilot

Inception is only the beginning. The pilot also showed that a strong Notebook
depends on extraction classes beyond ordinary claims.

The most useful additions were:

- definitions
- qualifications
- constraints
- contrasts/distinctions
- quote candidates
- source-role weighting

Those should be treated as part of the normal Notebook operating model, not as
optional polish after inception.

## Expected artifact inventory

At minimum, the first successful inception run should leave:

```text
natural-selection/
  manifests/source-manifest.yaml
  normalized/doclift/...
  citegeist/library.sqlite3
  citegeist/notebook-bundle/notebook_topic_bundle.json
  citegeist/notebook-bundle/notebook_topic_bibliography.bib
  groundrecall/store/...
  groundrecall/export/groundrecall_query_bundle.json
  didactopus/notebook-page/notebook_page.json
```

## Recommended immediate next actions

1. Create the pilot workspace directory and `source-manifest.yaml`.
2. Pick the exact textbook sections and one small web snapshot.
3. Run one small `doclift` normalization pass.
4. Seed one `CiteGeist` pilot database.
5. Build one real `GroundRecall` concept neighborhood for `natural-selection`.
6. Export the first real `notebook_page.json`.

## Bottom line

The Foundation Notebook is now blocked more by pilot execution than by missing
infrastructure. The first real threshold is not "build more Notebook code". It
is "produce the first real Notebook page artifact from provisioned, reviewed,
local sources".
