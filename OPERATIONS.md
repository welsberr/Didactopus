# Didactopus Operations

This is the operator entry point for the repository. Every command in the base
workflow runs from this checkout and does not require a sibling website,
course, or knowledge repository.

## Ownership boundary

Didactopus owns:

- Python packaging and its command-line, API, and MCP entry points
- pack ingestion, validation, review, promotion, and learner workflows
- model-provider configuration and inspection
- learning-sequence and reasoning-scaffold consumer contracts
- self-contained examples and regression tests for those contracts
- the review workbench source and build configuration

Optional producers own their source corpora, rendered pages, deployment
credentials, website build, and publication process. GroundRecall, CiteGeist,
doclift, GenieHive, and course or website repositories are integrations. None
is an implicit filesystem dependency of the base test or demo path.

Epistemap is a core Python library dependency rather than an implicit sibling
checkout. Until it has a package-index release, `pyproject.toml` resolves it
from an immutable commit in its public GitHub repository.

## Install and verify

Use Python 3.10 or newer:

```bash
python -m pip install -e '.[dev]'
make check
```

`make check` runs critical static checks (syntax and execution-breaking name
errors) and the complete Python test suite. CI runs the same checks from a
clean checkout. Broader style cleanup is intentionally outside this baseline.

## Run the core surfaces

Inspect the CLI:

```bash
didactopus --help
```

Run the API or MCP adapter:

```bash
didactopus-api
didactopus-mcp
```

Inspect a model route without starting a learning session:

```bash
didactopus provider-inspect --config configs/config.example.yaml
```

Run the included end-to-end learning demo:

```bash
python -m didactopus.ocw_information_entropy_demo
python -m didactopus.learner_session_demo
```

## Consume a learning sequence

The default command uses only repository-owned artifacts:

```bash
didactopus sequence-plan
```

The local contract fixture contains a sequence, a selection policy, and
concept-local scaffold records:

```text
examples/notebook-learning-sequence/
├── concepts/
└── learning-paths/
```

An external producer can use the same capability without adopting Didactopus
internals:

```bash
didactopus sequence-plan \
  --sequence /path/to/export/learning-paths/course.didactopus.json \
  --notebook-root /path/to/export \
  --selection-policy /path/to/export/learning-paths/course.selection-policy.json
```

The producer supplies data; Didactopus resolves and consumes it. The supported
sequence schema is `didactopus.notebook.learning_sequence.v1`. The earlier
site-specific schema name remains readable for compatibility but is not
emitted by repository fixtures.

Each sequence step may provide either:

- `scaffold_path`, relative to `--notebook-root`; or
- an HTML `url`, mapped to a sibling `.scaffold.json` path below that root.

Resolved scaffold paths are constrained to the configured root. Use an empty
`--selection-policy` value when no ranking policy is available.

## Review workbench

The frontend is independently buildable from this checkout:

```bash
cd webui
npm install
npm run build
```

The example Evidence Trail pack is repository data. Its original source URLs
remain in the compliance manifest as provenance, not as runtime dependencies.

## External publication

Didactopus deliberately does not embed a remote host, public web root, SSH
alias, or website allowlist. A publishing repository should:

1. generate a reviewed artifact bundle;
2. run its own public-surface and privacy checks;
3. call `didactopus sequence-plan` or the Python API as a consumer check when
   appropriate;
4. publish through that repository's reviewed deployment process.

This keeps deployments explicit and prevents one example website from becoming
Didactopus's operating environment.
