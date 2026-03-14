import React, { useEffect, useMemo, useState } from "react";
import { applyEvidence, buildMasteryMap, claimReadiness, milestoneMessages, progressPercent, recommendNext } from "./engine";
import { loadLearnerState, saveLearnerState, resetLearnerState } from "./storage";

const PACKS = ["/packs/bayes-pack.json", "/packs/stats-pack.json"];

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

export default function App() {
  const [packs, setPacks] = useState([]);
  const [selectedDomainId, setSelectedDomainId] = useState("");
  const [learnerName, setLearnerName] = useState("Wesley");
  const [domainStates, setDomainStates] = useState({});
  const [lastReward, setLastReward] = useState("");

  useEffect(() => {
    Promise.all(PACKS.map((u) => fetch(u).then((r) => r.json()))).then((loaded) => {
      setPacks(loaded);
      setSelectedDomainId(loaded[0]?.id || "");
      const states = {};
      for (const pack of loaded) {
        states[pack.id] = loadLearnerState(pack.id);
      }
      setDomainStates(states);
    });
  }, []);

  const domain = useMemo(() => packs.find((d) => d.id === selectedDomainId) || null, [packs, selectedDomainId]);
  const learnerState = domain ? (domainStates[domain.id] || loadLearnerState(domain.id)) : null;

  const masteryMap = useMemo(() => domain && learnerState ? buildMasteryMap(learnerState, domain) : [], [learnerState, domain]);
  const progress = useMemo(() => domain && learnerState ? progressPercent(learnerState, domain) : 0, [learnerState, domain]);
  const recs = useMemo(() => domain && learnerState ? recommendNext(learnerState, domain) : [], [learnerState, domain]);
  const milestones = useMemo(() => domain && learnerState ? milestoneMessages(learnerState, domain) : [], [learnerState, domain]);
  const readiness = useMemo(() => domain && learnerState ? claimReadiness(learnerState, domain) : {ready:false, mastered:0, avgScore:0, avgConfidence:0}, [learnerState, domain]);

  function updateState(domainId, nextState) {
    saveLearnerState(domainId, nextState);
    setDomainStates((prev) => ({ ...prev, [domainId]: nextState }));
  }

  function simulateStep(step) {
    if (!domain || !learnerState) return;
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
    updateState(domain.id, updated);
    setLastReward(step.reward);
  }

  function resetSelectedDomain() {
    if (!domain) return;
    resetLearnerState(domain.id);
    updateState(domain.id, loadLearnerState(domain.id));
    setLastReward("");
  }

  if (!domain || !learnerState) {
    return <div className="page"><div className="card">Loading packs...</div></div>;
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learner prototype</h1>
          <p>Real pack files, persistent learner state, and live recommendation updates.</p>
        </div>
        <div className="hero-controls">
          <label>
            Learner name
            <input value={learnerName} onChange={(e) => setLearnerName(e.target.value)} />
          </label>
          <button onClick={resetSelectedDomain}>Reset selected domain</button>
        </div>
      </header>

      <section className="domain-grid">
        {packs.map((d) => <DomainCard key={d.id} domain={d} selected={d.id === domain.id} onSelect={setSelectedDomainId} />)}
      </section>

      <main className="layout">
        <div className="left-col">
          <section className="card">
            <h2>First-session onboarding</h2>
            <h3>{domain.onboarding.headline}</h3>
            <p>{domain.onboarding.body}</p>
            <p className="muted">Learner: {learnerName || "Unnamed learner"}</p>
            <ul>{domain.onboarding.checklist.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
          </section>

          <section className="card">
            <h2>Visible mastery map</h2>
            <div className="map-grid">
              {masteryMap.map((node) => (
                <div key={node.id} className={`map-node ${node.status}`}>
                  <div className="node-label">{node.label}</div>
                  <div className="node-status">{node.status}</div>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <h2>Evidence log</h2>
            {learnerState.history.length === 0 ? <div className="muted">No evidence recorded yet.</div> : (
              <ul>
                {learnerState.history.slice().reverse().map((item, idx) => (
                  <li key={idx}>{item.concept_id} · score {item.score.toFixed(2)} · confidence hint {item.confidence_hint.toFixed(2)}</li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <div className="center-col">
          <section className="card">
            <h2>What should I do next?</h2>
            {recs.length === 0 ? (
              <div className="muted">No immediate recommendation available.</div>
            ) : (
              <div className="steps-stack">
                {recs.map((step) => <NextStepCard key={step.id} step={step} onSimulate={simulateStep} />)}
              </div>
            )}
          </section>
        </div>

        <div className="right-col">
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

          <section className="card">
            <h2>Milestones and rewards</h2>
            {lastReward ? <div className="reward-banner">{lastReward}</div> : null}
            <ul>{milestones.map((m, idx) => <li key={idx}>{m}</li>)}</ul>
          </section>

          <section className="card">
            <h2>Source attribution and compliance</h2>
            <div className="compliance-grid">
              <div><strong>Sources</strong><br />{domain.compliance.sources}</div>
              <div><strong>Attribution</strong><br />{domain.compliance.attributionRequired ? "required" : "not required"}</div>
              <div><strong>Share-alike</strong><br />{domain.compliance.shareAlikeRequired ? "yes" : "no"}</div>
              <div><strong>Noncommercial</strong><br />{domain.compliance.noncommercialOnly ? "yes" : "no"}</div>
            </div>
            <div className="flag-row">
              {domain.compliance.flags.length ? domain.compliance.flags.map((f) => <span className="flag" key={f}>{f}</span>) : <span className="muted">No extra flags</span>}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
