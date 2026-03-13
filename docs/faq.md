# FAQ

## Why multi-source ingestion?

Because course structure is usually distributed across several files rather than
perfectly contained in one source.

## What kinds of conflicts can arise?

Common examples:
- the same lesson with slightly different titles
- inconsistent terminology across notes and transcripts
- exercises present in one source but absent in another
- project prompts implied in one file and explicit in another

## Does the system resolve all conflicts automatically?

No. It produces a merged draft pack and a conflict report for human review.

## Why not rely only on embeddings for this?

Because Didactopus needs explicit structures such as:
- concepts
- prerequisites
- projects
- rubrics
- checkpoints
