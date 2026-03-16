# MIT OCW 6.050J Information and Entropy: Unit Sequence

Source: https://ocw.mit.edu/courses/6-050j-information-and-entropy-spring-2008/pages/syllabus/
Attribution: adapted from the MIT OpenCourseWare unit progression and resource organization for 6.050J Information and Entropy.

## Foundations

### Counting and Probability
- Objective: Explain how counting arguments, probability spaces, and random variables support later information-theory results.
- Exercise: Derive a simple counting argument for binary strings and compute an event probability.
Early units establish counting, combinatorics, and probability as the language used to reason about uncertainty, messages, and evidence.

### Shannon Entropy
- Objective: Explain Shannon entropy as a measure of uncertainty and compare high-entropy and low-entropy sources.
- Exercise: Compute the entropy of a Bernoulli source and interpret the result.
The course then introduces entropy as a quantitative measure of uncertainty for a source model and uses it to reason about representation cost and surprise.

### Mutual Information
- Objective: Explain mutual information and relate it to dependence between signals or observations.
- Exercise: Compare independent variables with dependent variables using mutual-information reasoning.
These units ask the learner to understand how observation changes uncertainty and what it means for one variable to carry information about another.

## Coding and Compression

### Source Coding and Compression
- Objective: Explain lossless compression in terms of entropy, redundancy, and coding choices.
- Exercise: Describe when compression succeeds and when it fails on already-random data.
The course develops the idea that structured sources can often be described more efficiently, but only up to limits implied by entropy.

### Huffman Coding
- Objective: Explain Huffman coding and justify why likely symbols receive shorter descriptions.
- Exercise: Build a Huffman code for a small source alphabet.
Learners use trees and expected length arguments to connect probability models to practical code design.

## Communication Under Noise

### Channel Capacity
- Objective: Explain channel capacity as a limit on reliable communication over a noisy channel.
- Exercise: State why reliable transmission above capacity is impossible in the long run.
The course treats capacity as a fundamental upper bound and frames noisy communication in terms of rates, inference, and uncertainty reduction.

### Channel Coding
- Objective: Explain how channel coding adds redundancy to protect messages from noise.
- Exercise: Contrast uncoded transmission with coded transmission on a noisy channel.
These units emphasize that redundancy can be wasteful in compression but essential in communication under uncertainty.

### Error Correcting Codes
- Objective: Explain how error-correcting codes detect or repair corrupted symbols.
- Exercise: Describe a simple parity-style code and its limits.
The learner must connect abstract limits to concrete coding mechanisms and understand both strengths and failure modes.

## Broader Applications

### Cryptography and Information Hiding
- Objective: Explain the relationship between secrecy, information leakage, and coded communication.
- Exercise: Compare a secure scheme with a weak one in terms of revealed information.
The course extends information-theoretic reasoning to adversarial settings where controlling what an observer can infer becomes central.

### Thermodynamics and Entropy
- Objective: Explain how thermodynamic entropy relates to, and differs from, Shannon entropy.
- Exercise: Compare the two entropy notions and identify what is preserved across the analogy.
The course uses entropy as a bridge concept between communication theory and physics while insisting on careful interpretation.

### Reversible Computation and Quantum Computation
- Objective: Explain why the physical implementation of computation matters for information processing limits.
- Exercise: Summarize how reversible computation changes the discussion of dissipation and information loss.
Later units connect information, entropy, and computation more directly by considering reversible logic, irreversibility, and quantum information themes.

### Course Synthesis
- Objective: Synthesize the course by connecting entropy, coding, reliability, secrecy, and physical interpretation in one coherent narrative.
- Exercise: Produce a final study guide that links source coding, channel coding, secrecy, thermodynamic analogies, and computation.
The end of the course asks the learner to unify the mathematical and physical perspectives rather than treating the units as disconnected topics.
