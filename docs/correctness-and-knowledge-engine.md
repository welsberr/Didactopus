# Correctness Evaluation and the Case for a Knowledge Engine

## Question

Is there a need for a more formal knowledge-engine component in Didactopus?

## Answer

Probably yes, in at least some target domains.

The current evidence and mastery layers are useful, but they remain fundamentally evaluation orchestrators. They can aggregate evidence, compare it to thresholds, and guide learning. What they cannot yet do, in a principled way, is guarantee correctness when the domain itself has strong formal structure.

## Why a formal layer may be needed

Some domains support correctness checks that are not merely stylistic or heuristic.

Examples:
- algebraic manipulation
- probability identities
- code execution and tests
- type checking
- formal logic
- graph constraints
- unit analysis
- finite-state or rule-based systems
- regulatory checklists with explicit conditions

In those cases, LLM-style evaluation should not be the only correctness mechanism.

## Recommended architecture

A future Didactopus should likely use a hybrid stack:

### 1. Generative / agentic layer
Responsible for:
- explanation
- synthesis
- dialogue
- critique
- problem decomposition
- exploratory hypothesis generation

### 2. Formal knowledge engine
Responsible for:
- executable validation
- symbolic checking
- proof obligations
- rule application
- constraint checking
- test execution
- ontology-backed consistency checks

## Possible forms of knowledge engine

Depending on domain, the formal component might include:
- theorem provers
- CAS systems
- unit and dimension analyzers
- typed AST analyzers
- code test harnesses
- Datalog or rule engines
- OWL/RDF/description logic tooling
- Bayesian network or probabilistic programming validators
- DSL interpreters for domain constraints

## Where it fits in Didactopus

The knowledge engine would sit beneath the evidence layer.

Possible flow:
1. learner produces an answer, explanation, proof sketch, program, or model
2. Didactopus extracts evaluable claims or artifacts
3. formal engine checks what it can check
4. agentic evaluator interprets the result and turns it into evidence
5. mastery state updates accordingly

## Why this matters for AI students

For agentic AI learners especially, formal validation is important because it reduces the risk that a fluent but incorrect model is credited with mastery.

## Conclusion

Didactopus does not strictly require a formal knowledge engine to be useful. But for many serious domains, adding one would materially improve:
- correctness
- trustworthiness
- transfer assessment
- deployment readiness
