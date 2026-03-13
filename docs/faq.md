# FAQ

## What is Didactopus?

Didactopus is a mastery-oriented learning infrastructure that uses concept graphs, evidence-based assessment, and adaptive planning to support serious learning.

## Is this just a tutoring chatbot?

No. The intended architecture is broader than tutoring. Didactopus maintains explicit representations of:
- concepts
- prerequisites
- mastery criteria
- evidence
- learner state
- planning priorities

## How is an AI student's learned mastery represented?

An AI student's learned mastery is represented as structured state, not just conversation history.

Important elements include:
- mastered concept set
- evidence records
- dimension-level competence summaries
- weak-dimension lists
- project eligibility
- target-progress state
- produced artifacts and critiques

## Does Didactopus fine-tune the AI model?

Not in the current design. Didactopus supervises and evaluates a learner agent, but it does not itself retrain foundation model weights.

## Then how is the AI student “ready to work”?

Readiness is operationalized by the mastery state. An AI student is ready for a class of tasks when:
- relevant concepts are mastered
- confidence is high enough
- weak dimensions are acceptable for the target task
- prerequisite and project evidence support deployment

## Could mastered state be exported?

Yes. A future implementation should support export of:
- concept mastery ledgers
- evidence portfolios
- competence profiles
- project artifacts
- domain-specific capability summaries

## Is human learning treated the same way?

The same conceptual framework applies to both human and AI learners, though interfaces and evidence sources differ.

## What is the difference between mastery and model knowledge?

A model may contain latent knowledge or pattern familiarity. Didactopus mastery is narrower and stricter: it is evidence-backed demonstrated competence with respect to explicit concepts and criteria.

## Why not use only embeddings and LLM judgments?

Because correctness, especially in formal domains, often needs stronger guarantees than plausibility. That is why Didactopus may eventually need hybrid symbolic or executable validation components.

## Can Didactopus work offline?

Yes, that is a primary design goal. The architecture is local-first and can be paired with local model serving and locally stored domain packs.
