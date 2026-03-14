# Synthesis Engine Architecture

## Purpose

The synthesis engine identifies potentially useful conceptual overlaps across
packs, topics, and learning trajectories. Its goal is to help learners and
maintainers discover connections that improve understanding of the topic of
interest.

This is not merely a recommendation engine. It is a **cross-domain structural
discovery system**.

---

## Design goals

- identify meaningful connections across packs
- support analogy, transfer, and hidden-prerequisite discovery
- generate reviewer-friendly candidate proposals
- improve pack quality and curriculum design
- capture surprising learner or AI discoveries
- expose synthesis to users visually and operationally

---

## Kinds of synthesis targets

### 1. Cross-pack concept similarity
Examples:
- entropy ↔ entropy
- drift ↔ random walk
- selection pressure ↔ optimization pressure

### 2. Structural analogy
Examples:
- feedback loops in control theory and ecology
- graph search and evolutionary exploration
- signal detection in acoustics and statistical inference

### 3. Hidden prerequisite discovery
If learners repeatedly fail on a concept despite nominal prerequisites, a
missing dependency may exist.

### 4. Example transfer
A concept may become easier to understand when illustrated by examples from
another pack.

### 5. Skill transfer
A skill bundle from one domain may partially apply in another domain.

---

## Data model

### ConceptNode
- concept_id
- pack_id
- title
- description
- prerequisites
- tags
- examples
- glossary terms
- vector embedding
- graph neighborhood signature

### SynthesisCandidate
- synthesis_id
- source_concept_id
- target_concept_id
- source_pack_id
- target_pack_id
- synthesis_kind
- score_total
- score_semantic
- score_structural
- score_trajectory
- score_review_history
- explanation
- evidence
- current_status

### SynthesisCluster
Represents a small group of mutually related concepts across packs.

Fields:
- cluster_id
- member_concepts
- centroid_embedding
- theme_label
- notes

### HiddenPrerequisiteCandidate
- source_concept_id
- suspected_missing_prerequisite_id
- signal_strength
- supporting_fail_patterns
- reviewer_status

---

## Scoring methods

The engine should combine multiple signals.

### A. Semantic similarity score
Source:
- concept text
- glossary
- examples
- descriptions
- optional embeddings

Methods:
- cosine similarity on embeddings
- term overlap
- phrase normalization
- ontology-aware synonyms if available

### B. Structural similarity score
Source:
- prerequisite neighborhoods
- downstream dependencies
- graph motif similarity
- role in pack topology

Examples:
- concepts that sit in similar graph positions
- concepts that unlock similar kinds of later work

### C. Learner trajectory score
Source:
- shared error patterns
- similar mastery progression
- evidence timing
- co-improvement patterns across learners

Examples:
- learners who master A often learn B faster
- failure on X predicts later trouble on Y

### D. Reviewer history score
Source:
- accepted past synthesis suggestions
- rejected patterns
- reviewer preference patterns

Use:
- prioritize candidate types with strong track record

### E. Novelty score
Purpose:
- avoid flooding reviewers with obvious or duplicate links

Methods:
- de-duplicate against existing pack links
- penalize near-duplicate proposals
- boost under-explored high-signal regions

---

## Composite score

Suggested first composite:

score_total =
    0.35 * semantic_similarity
  + 0.25 * structural_similarity
  + 0.20 * trajectory_signal
  + 0.10 * review_prior
  + 0.10 * novelty

This weighting should remain configurable.

---

## Discovery pipeline

### Step 1. Ingest graph and learner data
Inputs:
- packs
- concepts
- pack metadata
- learner states
- evidence histories
- artifacts
- knowledge exports

### Step 2. Compute concept features
For each concept:
- embedding
- prerequisite signature
- downstream signature
- learner-error signature
- example signature

### Step 3. Generate candidate pairs
Possible approaches:
- nearest neighbors in embedding space
- shared tag neighborhoods
- prerequisite motif matches
- frequent learner co-patterns

### Step 4. Re-rank candidates
Combine semantic, structural, and trajectory scores.

### Step 5. Group into synthesis clusters
Cluster related candidate pairs into themes such as:
- uncertainty
- feedback
- optimization
- conservation
- branching processes

### Step 6. Produce explanations
Each candidate should include a compact explanation, for example:
- “These concepts occupy similar prerequisite roles.”
- “Learner error patterns suggest a hidden shared dependency.”
- “Examples in pack A may clarify this concept in pack B.”

### Step 7. Send to review-and-promotion workflow
All candidates become reviewable objects rather than immediately modifying packs.

---

## Outputs

The engine should emit candidate objects suitable for promotion into:

- cross-pack links
- pack improvement suggestions
- curriculum draft notes
- skill-bundle drafts
- archived synthesis notes

---

## UI visualization

### 1. Synthesis map
Graph overlay showing:
- existing cross-pack links
- proposed synthesis links
- confidence levels
- accepted vs candidate status

### 2. Candidate explanation panel
For a selected proposed link:
- why it was suggested
- component scores
- source evidence
- similar accepted proposals
- reviewer actions

### 3. Cluster view
Shows higher-level themes connecting multiple packs.

### 4. Learner pathway overlay
Allows a maintainer to see where synthesis would help a learner currently stuck in
one pack by borrowing examples or structures from another.

### 5. Promotion workflow integration
Every synthesis candidate can be:
- accepted as pack improvement
- converted to curriculum draft
- converted to skill bundle
- archived
- rejected

---

## Appropriate uses

The synthesis engine is especially useful for:

- interdisciplinary education
- transfer learning support
- AI learner introspection
- pack maintenance
- curriculum design
- discovery of hidden structure

---

## Cautions

- synthesis suggestions are candidate aids, not guaranteed truths
- semantic similarity alone is not enough
- over-linking can confuse learners
- reviewers need concise explanation and provenance
- accepted synthesis should be visible as intentional structure, not accidental clutter
