import React, { useMemo, useState } from "react";
import { domains } from "./domainData";
import {
  applyEvidence,
  buildMasteryMap,
  claimReadiness,
  milestoneMessages,
  progressPercent,
  recommendNext,
  starterLearnerState
} from "./engine";

function DomainCard({ domain, selected, onSelect }) {
  return (
    <button className={`domain-card ${selected ? "selected" : ""}`} onClick={() => onSelect(domain.id)}>
      <div className="domain-title">{domain.title}</div>
      <div className="domain-subtitle">{domain.subtitle}</div>
      <div className="domain-meta">
        <span>{domain.level}</span>
        <span>{domain.concepts.length} concepts</span>
      </div>
    </button>
  );
}

function OnboardingPanel({ domain, learnerName }) {
  return (
    <section className="card">
      <h2>First-session onboarding</h2>
      <h3>{domain.onboarding.headline}</h3>
      <p>{domain.onboarding.body}</p>
      <p className="muted">Learner: {learnerName || "Unnamed learner"}</p>
      <ul>
        {domain.onboarding.checklist.map((item, idx) => <li key={idx}>{item}</li>)}
      </ul>
    </section>
  );
}

function NextStepCard({ step, onSimulate }) {
  return (
    <div className="step-card">
      <div className="step-header">
        <div>
          <h3>{step.title}</h3>
          <div className="muted">{step.minutes} minutes</div>
        </div>
        <div className="reward-pill">{step.reward}</div>
      </div>
      <p>{step.reason}</p>
      <details>
        <summary>Why this is recommended</summary>
        <ul>
          {step.why.map((item, idx) => <li key={idx}>{item}</li>)}
        </ul>
      </details>
      <button className="primary" onClick={() => onSimulate(step)}>Simulate completing this step</button>
    </div>
  );
}

function MasteryMap({ nodes }) {
  return (
    <section className="card">
      <h2>Visible mastery map</h2>
      <div className="map-grid">
        {nodes.map((node) => (
          <div key={node.id} className={`map-node ${node.status}`}>
            <div className="node-label">{node.label}</div>
            <div className="node-status">{node.status}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ProgressPanel({ progress, readiness }) {
  return (
    <section className="card">
      <h2>Progress</h2>
      <div className="progress-wrap">
        <div className="progress-label">Mastery progress</div>
        <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }} /></div>
        <div className="muted">{progress}%</div>
      </div>
      <div className={`readiness-box ${readiness.ready ? "ready" : ""}`}>
        <strong>{readiness.ready ? "Usable expertise threshold met" : "Still building toward usable expertise"}</strong>
        <div className="muted">Mastered concepts: {readiness.mastered}</div>
        <div className="muted">Average score: {readiness.avgScore.toFixed(2)}</div>
        <div className="muted">Average confidence: {readiness.avgConfidence.toFixed(2)}</div>
      </div>
    </section>
  );
}

function MilestonePanel({ milestones, lastReward }) {
  return (
    <section className="card">
      <h2>Milestones and rewards</h2>
      {lastReward ? <div className="reward-banner">{lastReward}</div> : null}
      <ul>
        {milestones.map((m, idx) => <li key={idx}>{m}</li>)}
      </ul>
    </section>
  );
}

function CompliancePanel({ compliance }) {
  return (
    <section className="card">
      <h2>Source attribution and compliance</h2>
      <div className="compliance-grid">
        <div><strong>Sources</strong><br />{compliance.sources}</div>
        <div><strong>Attribution</strong><br />{compliance.attributionRequired ? "required" : "not required"}</div>
        <div><strong>Share-alike</strong><br />{compliance.shareAlikeRequired ? "yes" : "no"}</div>
        <div><strong>Noncommercial</strong><br />{compliance.noncommercialOnly ? "yes" : "no"}</div>
      </div>
      <div className="flag-row">
        {compliance.flags.length ? compliance.flags.map((f) => <span className="flag" key={f}>{f}</span>) : <span className="muted">No extra flags</span>}
      </div>
      <p className="muted">
        Provenance-sensitive packs should remain inspectable so that learners and maintainers do not have to guess at reuse constraints.
      </p>
    </section>
  );
}

function EvidenceLog({ history }) {
  return (
    <section className="card">
      <h2>Evidence log</h2>
      {history.length === 0 ? (
        <div className="muted">No evidence recorded yet.</div>
      ) : (
        <ul>
          {history.slice().reverse().map((item, idx) => (
            <li key={idx}>
              {item.concept_id} · score {item.score.toFixed(2)} · confidence hint {item.confidence_hint.toFixed(2)}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function App() {
  const [learnerName, setLearnerName] = useState("Wesley");
  const [selectedDomainId, setSelectedDomainId] = useState(domains[0].id);
  const [domainStates, setDomainStates] = useState(() =>
    Object.fromEntries(domains.map((d) => [d.id, starterLearnerState(`learner-${d.id}`)]))
  );
  const [lastReward, setLastReward] = useState("");

  const domain = useMemo(() => domains.find((d) => d.id === selectedDomainId) || domains[0], [selectedDomainId]);
  const learnerState = domainStates[selectedDomainId];

  const masteryMap = useMemo(() => buildMasteryMap(learnerState, domain), [learnerState, domain]);
  const progress = useMemo(() => progressPercent(learnerState, domain), [learnerState, domain]);
  const recs = useMemo(() => recommendNext(learnerState, domain), [learnerState, domain]);
  const milestones = useMemo(() => milestoneMessages(learnerState, domain), [learnerState, domain]);
  const readiness = useMemo(() => claimReadiness(learnerState, domain), [learnerState, domain]);

  function simulateStep(step) {
    const timestamp = new Date().toISOString();
    const updated = applyEvidence(learnerState, {
      concept_id: step.conceptId,
      dimension: "mastery",
      score: step.scoreHint,
      confidence_hint: step.confidenceHint,
      timestamp,
      kind: "checkpoint",
      source_id: `ui-${step.id}`
    });
    setDomainStates((prev) => ({ ...prev, [selectedDomainId]: updated }));
    setLastReward(step.reward);
  }

  function resetDomain() {
    setDomainStates((prev) => ({ ...prev, [selectedDomainId]: starterLearnerState(`learner-${selectedDomainId}`) }));
    setLastReward("");
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learner prototype</h1>
          <p>
            Pick a topic, get a clear onboarding path, see live progress, and inspect exactly why the system recommends each next step.
          </p>
        </div>
        <div className="hero-controls">
          <label>
            Learner name
            <input value={learnerName} onChange={(e) => setLearnerName(e.target.value)} />
          </label>
          <button onClick={resetDomain}>Reset selected domain</button>
        </div>
      </header>

      <section className="domain-grid">
        {domains.map((d) => (
          <DomainCard key={d.id} domain={d} selected={d.id === domain.id} onSelect={setSelectedDomainId} />
        ))}
      </section>

      <main className="layout">
        <div className="left-col">
          <OnboardingPanel domain={domain} learnerName={learnerName} />
          <MasteryMap nodes={masteryMap} />
          <EvidenceLog history={learnerState.history} />
        </div>

        <div className="center-col">
          <section className="card">
            <h2>What should I do next?</h2>
            {recs.length === 0 ? (
              <div className="muted">No immediate recommendation available. You may have completed the current progression or need a new pack.</div>
            ) : (
              <div className="steps-stack">
                {recs.map((step) => <NextStepCard key={step.id} step={step} onSimulate={simulateStep} />)}
              </div>
            )}
          </section>
        </div>

        <div className="right-col">
          <ProgressPanel progress={progress} readiness={readiness} />
          <MilestonePanel milestones={milestones} lastReward={lastReward} />
          <CompliancePanel compliance={domain.compliance} />
        </div>
      </main>
    </div>
  );
}
