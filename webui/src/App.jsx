import React, { useEffect, useMemo, useState } from "react";
import { fetchPacks, fetchLearnerState, fetchRecommendations, postEvidence } from "./api";
import { buildMasteryMap, progressPercent, milestoneMessages, claimReadiness } from "./localEngine";

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
        <ul>{step.why.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
      </details>
      <button className="primary" onClick={() => onSimulate(step)}>Simulate completing this step</button>
    </div>
  );
}

export default function App() {
  const [packs, setPacks] = useState([]);
  const [selectedDomainId, setSelectedDomainId] = useState("");
  const [learnerName, setLearnerName] = useState("Wesley");
  const [learnerState, setLearnerState] = useState(null);
  const [cards, setCards] = useState([]);
  const [lastReward, setLastReward] = useState("");
  const learnerId = "wesley-demo";

  useEffect(() => {
    async function load() {
      const loadedPacks = await fetchPacks();
      setPacks(loadedPacks);
      const first = loadedPacks[0]?.id || "";
      setSelectedDomainId(first);
      const state = await fetchLearnerState(learnerId);
      setLearnerState(state);
    }
    load();
  }, []);

  useEffect(() => {
    async function loadCards() {
      if (!selectedDomainId) return;
      const data = await fetchRecommendations(learnerId, selectedDomainId);
      setCards(data.cards || []);
    }
    if (selectedDomainId) loadCards();
  }, [selectedDomainId, learnerState]);

  const domain = useMemo(() => packs.find((d) => d.id === selectedDomainId) || null, [packs, selectedDomainId]);
  const masteryMap = useMemo(() => domain && learnerState ? buildMasteryMap(learnerState, domain) : [], [learnerState, domain]);
  const progress = useMemo(() => domain && learnerState ? progressPercent(learnerState, domain) : 0, [learnerState, domain]);
  const milestones = useMemo(() => domain && learnerState ? milestoneMessages(learnerState, domain) : [], [learnerState, domain]);
  const readiness = useMemo(() => domain && learnerState ? claimReadiness(learnerState, domain) : {ready:false, mastered:0, avgScore:0, avgConfidence:0}, [learnerState, domain]);

  async function simulateStep(step) {
    const nextState = await postEvidence(learnerId, {
      concept_id: step.conceptId,
      dimension: "mastery",
      score: step.scoreHint,
      confidence_hint: step.confidenceHint,
      timestamp: new Date().toISOString(),
      kind: "checkpoint",
      source_id: `ui-${step.id}`
    });
    setLearnerState(nextState);
    setLastReward(step.reward);
  }

  if (!domain || !learnerState) {
    return <div className="page"><div className="card">Loading backend data...</div></div>;
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learner prototype</h1>
          <p>Backend-driven pack registry, learner-state persistence, and evaluator-style evidence ingestion.</p>
        </div>
        <div className="hero-controls">
          <label>
            Learner name
            <input value={learnerName} onChange={(e) => setLearnerName(e.target.value)} />
          </label>
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
            <p className="muted">Learner: {learnerName}</p>
            <ul>{(domain.onboarding.checklist || []).map((item, idx) => <li key={idx}>{item}</li>)}</ul>
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
            {cards.length === 0 ? <div className="muted">No immediate recommendation available.</div> : (
              <div className="steps-stack">
                {cards.map((step) => <NextStepCard key={step.id} step={step} onSimulate={simulateStep} />)}
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
