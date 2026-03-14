# Didactopus

This update adds a **coverage-and-alignment QA layer**.

It checks whether concepts, mastery signals, checkpoints, projects, and rubrics
actually line up well enough to support a credible mastery path.

Current checks:
- concepts absent from roadmap stages
- concepts absent from checkpoint language
- concepts absent from project prerequisites
- concepts never covered by either checkpoints or projects
- mastery signals not reflected in checkpoints or deliverables
- rubric criteria with weak overlap to mastery/project language
- projects that cover too little of the concept set
