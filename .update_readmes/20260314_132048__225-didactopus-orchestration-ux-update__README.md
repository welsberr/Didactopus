# Didactopus

This update adds a **learner-run orchestration layer scaffold** with explicit **UX design guidance**.

The goal is to tie together:
- domain-pack selection
- learner onboarding
- recommendation generation
- evaluator invocation
- mastery-ledger updates
- stopping criteria for usable expertise
- humane, low-friction user experience

## UX stance

Didactopus should not require the learner to first master Didactopus.

A person approaching a new topic should be able to:
- choose a topic
- understand what to do next
- get feedback quickly
- see progress clearly
- recover easily from mistakes or uncertainty
- experience the process as rewarding rather than bureaucratic

## UX principles

### 1. Low activation energy
The first session should produce visible progress quickly.

### 2. Clear next action
At every point, the learner should know what to do next.

### 3. Gentle structure
The system should scaffold without becoming oppressive or confusing.

### 4. Reward loops
Progress should feel visible and meaningful:
- concept unlocks
- streaks or milestones
- mastery-map filling
- capstone readiness indicators
- “you can now do X” style feedback

### 5. Human-readable state
The learner should be able to inspect:
- what the system thinks they know
- why it thinks that
- what evidence changed the estimate
- what is blocking advancement

### 6. Graceful fallback
When the system is uncertain, it should degrade into simple guidance, not inscrutable failure.

## Included in this update

- orchestration state models
- onboarding/session planning scaffold
- learner run-loop scaffold
- stop/claim-readiness criteria scaffold
- UX-oriented recommendation formatting
- sample CLI flow
- UX notes for future web UI work
