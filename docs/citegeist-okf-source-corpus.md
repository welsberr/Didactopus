# CiteGeist OKF Source Corpus

Didactopus can use a CiteGeist OKF topic bundle as source material for learner-facing packs and workspaces.

Create the CiteGeist bundle:

```bash
citegeist --db library.sqlite3 export-okf --topic TOPIC --output-dir topic-okf
```

Convert it into Didactopus source-corpus artifacts:

```bash
python -m didactopus.main citegeist-okf-source-corpus topic-okf didactopus-source
```

The command writes:

- `source_corpus.json`, containing CiteGeist works as sources and bibliographic summaries/abstracts as fragments;
- `resources.md`, a human-readable reading list;
- `citegeist_okf_import_manifest.json`, a small manifest for the generated artifacts.

This keeps bibliography verification in CiteGeist while allowing Didactopus packs to carry curated, reviewed literature context as supporting source material.
