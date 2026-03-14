# Didactopus Worker-Backed Artifact Registry Layer

This update extends the media-rendering pipeline with a **worker-backed artifact registry**.

## What it adds

- artifact registry records
- render job records
- worker-oriented job lifecycle states
- artifact listing and lookup endpoints
- bundle registration into a persistent catalog
- UI prototype for browsing render jobs and produced artifacts

## Why this matters

The previous layer could create render bundles, but the outputs were still basically
filesystem-level side effects. This layer promotes artifacts into first-class Didactopus
objects so the system can:

- track render requests over time
- associate artifacts with learners and packs
- record job status (`queued`, `running`, `completed`, `failed`)
- expose artifacts in the UI and API
- support future download, retention, and publication policies
