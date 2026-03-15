# MIT OCW 6.050J Information and Entropy

Source: MIT OpenCourseWare 6.050J Information and Entropy, Spring 2008.
Attribution: adapted from the OCW course overview, unit sequence, and assigned textbook references.

## Foundations of Information Theory

### Counting and Probability
- Objective: Explain how counting arguments, probability spaces, and random variables support later information-theory results.
- Exercise: Derive a simple counting argument for binary strings and compute an event probability.
This lesson introduces Counting, Probability, Random Variables, and Combinatorics as the shared language for the rest of the course. The learner should connect these basics to uncertainty, messages, and evidence.

### Shannon Entropy
- Objective: Explain Shannon Entropy as a measure of uncertainty and compare high-entropy and low-entropy sources.
- Exercise: Compute the entropy of a Bernoulli source and interpret the result.
This lesson centers Shannon Entropy, Surprise, and Source Models. The learner should describe why entropy matters because it bounds efficient description length and clarifies uncertainty.

### Mutual Information
- Objective: Explain Mutual Information and relate it to dependence between signals.
- Exercise: Compare independent variables with dependent variables using mutual-information reasoning.
This lesson introduces Mutual Information, Dependence, and Observations. The learner should explain how information gain changes when observations reduce uncertainty.

## Compression and Source Coding

### Data Compression
- Objective: Explain lossless compression in terms of entropy and typical structure.
- Exercise: Describe when compression succeeds and when it fails on already-random data.
This lesson covers Data Compression, Redundancy, and Efficient Representation. The learner should connect entropy limits to coding choices.

### Huffman Coding
- Objective: Explain Huffman Coding and justify why shorter codewords should track more likely symbols.
- Exercise: Build a Huffman code for a small source alphabet.
This lesson focuses on Huffman Coding, Prefix Codes, and Expected Length. The learner should explain the tradeoff between probability, tree structure, and average code length.

### Channel Capacity
- Objective: Explain Channel Capacity as a limit on reliable communication over noisy channels.
- Exercise: State why reliable transmission above capacity is impossible in the long run.
This lesson develops Channel Capacity, Reliable Communication, and Noise. The learner should explain why capacity matters because it defines the ceiling for dependable transmission.

## Communication Under Noise

### Channel Coding
- Objective: Explain how Channel Coding adds structure that protects messages against noise.
- Exercise: Contrast uncoded transmission with coded transmission on a noisy channel.
This lesson connects Channel Coding, Decoding, and Reliability. The learner should explain the role of redundancy and inference in successful communication.

### Error Correcting Codes
- Objective: Explain how Error Correcting Codes detect or correct symbol corruption.
- Exercise: Describe a simple parity-style code and its limits.
This lesson covers Error Correcting Codes, Parity, and Syndrome-style reasoning. The learner should discuss strengths, failure modes, and decoding assumptions.

## Applications and Synthesis

### Cryptography and Information Hiding
- Objective: Explain the relationship between secrecy, information leakage, and coded communication.
- Exercise: Compare a secure scheme with a weak one in terms of revealed information.
This lesson combines Cryptography, Information Leakage, and Adversarial Observation. The learner should explain secrecy as controlled information flow rather than only obscurity.

### Thermodynamics and Entropy
- Objective: Explain how thermodynamic entropy relates to, and differs from, Shannon entropy.
- Exercise: Compare the two entropy notions and identify what is preserved across the analogy.
This lesson connects Thermodynamics, Entropy, and Physical Interpretation. The learner should explain the analogy carefully because the shared mathematics does not erase domain differences.

### Course Synthesis
- Objective: Synthesize the course by connecting entropy, coding, reliability, and physical interpretation in one coherent narrative.
- Exercise: Produce a final study guide that links source coding, channel coding, secrecy, and thermodynamic analogies.
This lesson integrates Source Coding, Channel Coding, Cryptography, and Thermodynamic Analogy. The learner should show how the course forms one unified model of uncertainty, representation, and communication.
