# Didactopus

**Didactopus** is a local‑first AI‑assisted autodidactic mastery platform designed to help motivated learners achieve **true expertise** in a chosen domain.

![Didactopus mascot](artwork/didactopus-mascot.png)

The system combines:

• domain knowledge graphs  
• mastery‑based learning models  
• evidence‑driven assessment  
• Socratic mentoring  
• adaptive curriculum generation  
• project‑based evaluation

Didactopus is designed for **serious learning**, not shallow answer generation.

Its core philosophy is:

> AI should function as a mentor, evaluator, and guide — not a substitute for thinking.

---

# Project Goals

Didactopus aims to enable learners to:

• build deep conceptual understanding  
• practice reasoning and explanation  
• complete real projects demonstrating competence  
• identify weak areas through evidence‑based feedback  
• progress through mastery rather than time spent

The platform is particularly suitable for:

• autodidacts  
• researchers entering new fields  
• students supplementing formal education  
• interdisciplinary learners  
• AI‑assisted self‑study programs

---

# Key Architectural Concepts

## Domain Packs

Knowledge is distributed as **domain packs** contributed by the community.

Each pack can include:

- concept definitions
- prerequisite graphs
- learning roadmaps
- projects
- rubrics
- mastery profiles

Example packs:

```
domain-packs/
    statistics-foundations
    bayes-extension
    applied-inference
```

Domain packs are validated, dependency‑checked, and merged into a **unified learning graph**.

---

# Learning Graph

Didactopus merges all installed packs into a directed concept graph:

```
Concept A → Concept B → Concept C
```

Edges represent prerequisites.

The system then generates:

• adaptive learning roadmaps  
• next-best concepts to study  
• projects unlocked by prerequisite completion

---

# Evidence‑Driven Mastery

Concept mastery is **inferred from evidence**, not declared.

Evidence types include:

• explanations  
• problem solutions  
• transfer tasks  
• project deliverables

Evidence contributes weighted scores that determine:

• mastery state  
• learner confidence  
• weak dimensions requiring further practice

---

# Multi‑Dimensional Mastery

Didactopus tracks multiple competence dimensions:

| Dimension | Meaning |
|---|---|
| correctness | accurate reasoning |
| explanation | ability to explain clearly |
| transfer | ability to apply knowledge |
| project_execution | ability to build artifacts |
| critique | ability to detect errors and assumptions |

Different concepts can require different combinations of these dimensions.

---

# Concept Mastery Profiles

Concepts define **mastery profiles** specifying:

• required dimensions  
• threshold overrides

Example:

```yaml
mastery_profile:
  required_dimensions:
    - correctness
    - transfer
    - critique
  dimension_threshold_overrides:
    transfer: 0.8
    critique: 0.8
```

---

# Mastery Profile Inheritance

This revision adds **profile templates** so packs can define reusable mastery models.

Example:

```yaml
profile_templates:
  foundation_concept:
    required_dimensions:
      - correctness
      - explanation

  critique_concept:
    required_dimensions:
      - correctness
      - transfer
      - critique
```

Concepts can reference templates:

```yaml
mastery_profile:
  template: critique_concept
```

This allows domain packs to remain concise while maintaining consistent evaluation standards.

---

# Adaptive Learning Engine

The adaptive engine computes:

• which concepts are ready to study  
• which are blocked by prerequisites  
• which are already mastered  
• which projects are available

Output includes:

```
next_best_concepts
eligible_projects
adaptive_learning_roadmap
```

---

# Evidence Engine

The evidence engine:

• aggregates learner evidence  
• computes weighted scores  
• tracks confidence  
• identifies weak competence dimensions  
• updates mastery status

Later weak performance can **resurface concepts for review**.

---

# Socratic Mentor

Didactopus includes a mentor layer that:

• asks probing questions  
• challenges reasoning  
• generates practice tasks  
• proposes projects

Models can run locally (recommended) or via remote APIs.

---

# Agentic AI Students

Didactopus is also suitable for **AI‑driven learning agents**.

A future architecture may include:

```
Didactopus Core
       │
       ├─ Human Learner
       └─ AI Student Agent
```

An AI student could:

1. read domain packs
2. attempt practice tasks
3. produce explanations
4. critique model outputs
5. complete simulated projects
6. accumulate evidence
7. progress through the mastery graph

Such agents could be used for:

• automated curriculum testing  
• benchmarking AI reasoning  
• synthetic expert generation  
• evaluation of model capabilities

Didactopus therefore supports both:

• human learners  
• agentic AI learners

---

# Project Structure

```
didactopus/
    adaptive_engine/
    artifact_registry/
    evidence_engine/
    learning_graph/
    mentor/
    practice/
    project_advisor/
```

Additional directories:

```
configs/
docs/
domain-packs/
tests/
artwork/
```

---

# Current Status

Implemented:

✓ domain pack validation  
✓ dependency resolution  
✓ learning graph merge  
✓ adaptive roadmap generation  
✓ evidence‑driven mastery  
✓ multi‑dimensional competence tracking  
✓ concept‑specific mastery profiles  
✓ profile template inheritance

Planned next phases:

• curriculum optimization algorithms  
• active‑learning task generation  
• automated project evaluation  
• distributed pack registry  
• visualization tools for learning graphs

---

# Philosophy

Didactopus is built around a simple principle:

> Mastery requires thinking, explaining, testing, and building — not merely receiving answers.

AI can accelerate the process, but genuine learning remains an **active intellectual endeavor**.

---

**Didactopus — many arms, one goal: mastery.**
