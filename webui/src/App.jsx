import React, { useEffect, useMemo, useState } from "react";
import { login, fetchPacks, createLearner, fetchLearnerState, fetchRecommendations, postEvidence, submitEvaluatorJob, fetchEvaluatorJob } from "./api";
import { buildMasteryMap, progressPercent } from "./localEngine";

function LoginPanel({ onLogin }) {
  const [username, setUsername] = useState("wesley");
  const [password, setPassword] = useState("demo-pass");
  const [error, setError] = useState("");

  async function handleLogin() {
    try {
      setError("");
      const result = await onLogin(username, password);
      return result;
    } catch (e) {
      setError("Login failed");
    }
  }

  return (
    <section className="card narrow">
      <h1>Didactopus login</h1>
      <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
      <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
      <button className="primary" onClick={handleLogin}>Login</button>
      {error ? <div className="error">{error}</div> : null}
    </section>
  );
}

function DomainCard({ domain, selected, onSelect }) {
  return (
    <button className={`domain-card ${selected ? "selected" : ""}`} onClick={() => onSelect(domain.id)}>
      <div className="domain-title">{domain.title}</div>
      <div className="domain-subtitle">{domain.subtitle}</div>
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
      <div className="button-row">
        <button className="primary" onClick={() => onSimulate(step)}>Simulate step</button>
      </div>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [packs, setPacks] = useState([]);
  const [selectedDomainId, setSelectedDomainId] = useState("");
  const [learnerId, setLearnerId] = useState("wesley-learner");
  const [learnerState, setLearnerState] = useState(null);
  const [cards, setCards] = useState([]);
  const [jobStatus, setJobStatus] = useState(null);

  async function handleLogin(user, pass) {
    const auth = await login(user, pass);
    setToken(auth.token);
    setUsername(auth.username);
    await createLearner(auth.token, learnerId, learnerId);
    const loadedPacks = await fetchPacks(auth.token);
    setPacks(loadedPacks);
    setSelectedDomainId(loadedPacks[0]?.id || "");
    const state = await fetchLearnerState(auth.token, learnerId);
    setLearnerState(state);
    return auth;
  }

  useEffect(() => {
    async function loadCards() {
      if (!token || !selectedDomainId) return;
      const data = await fetchRecommendations(token, learnerId, selectedDomainId);
      setCards(data.cards || []);
    }
    loadCards();
  }, [token, learnerId, selectedDomainId, learnerState]);

  const domain = useMemo(() => packs.find((d) => d.id === selectedDomainId) || null, [packs, selectedDomainId]);
  const masteryMap = useMemo(() => domain && learnerState ? buildMasteryMap(learnerState, domain) : [], [learnerState, domain]);
  const progress = useMemo(() => domain && learnerState ? progressPercent(learnerState, domain) : 0, [learnerState, domain]);

  async function simulateStep(step) {
    const nextState = await postEvidence(token, learnerId, {
      concept_id: step.conceptId,
      dimension: "mastery",
      score: step.scoreHint,
      confidence_hint: step.confidenceHint,
      timestamp: new Date().toISOString(),
      kind: "checkpoint",
      source_id: `ui-${step.id}`
    });
    setLearnerState(nextState);
  }

  async function submitDemoEvaluator() {
    if (!domain) return;
    const firstConcept = domain.concepts[0]?.id;
    const job = await submitEvaluatorJob(token, learnerId, {
      pack_id: domain.id,
      concept_id: firstConcept,
      submitted_text: "This is a moderately detailed learner response intended to trigger a somewhat better prototype evaluator score.",
      kind: "checkpoint"
    });
    setJobStatus(job);
    setTimeout(async () => {
      const refreshed = await fetchEvaluatorJob(token, job.job_id);
      setJobStatus(refreshed);
      const state = await fetchLearnerState(token, learnerId);
      setLearnerState(state);
    }, 1200);
  }

  if (!token) {
    return <div className="page"><LoginPanel onLogin={handleLogin} /></div>;
  }

  if (!domain || !learnerState) {
    return <div className="page"><div className="card">Loading authenticated learner view...</div></div>;
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learner prototype</h1>
          <p>Authenticated multi-user scaffold with DB-backed state and async evaluator jobs.</p>
          <div className="muted">Signed in as {username}</div>
        </div>
        <div className="hero-controls">
          <label>Learner ID<input value={learnerId} onChange={(e) => setLearnerId(e.target.value)} /></label>
          <button onClick={submitDemoEvaluator}>Submit demo evaluator job</button>
        </div>
      </header>

      <section className="domain-grid">
        {packs.map((d) => <DomainCard key={d.id} domain={d} selected={d.id === domain.id} onSelect={setSelectedDomainId} />)}
      </section>

      <main className="layout">
        <div className="left-col">
          <section className="card">
            <h2>Onboarding</h2>
            <h3>{domain.onboarding.headline}</h3>
            <p>{domain.onboarding.body}</p>
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
            <h2>Async evaluator job</h2>
            {jobStatus ? (
              <div>
                <div><strong>Status:</strong> {jobStatus.status}</div>
                <div><strong>Score:</strong> {jobStatus.result_score ?? "-"}</div>
                <div><strong>Confidence hint:</strong> {jobStatus.result_confidence_hint ?? "-"}</div>
                <div className="muted">{jobStatus.result_notes || ""}</div>
              </div>
            ) : (
              <div className="muted">No evaluator job submitted yet.</div>
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
          </section>

          <section className="card">
            <h2>Evidence log</h2>
            {learnerState.history.length === 0 ? <div className="muted">No evidence recorded yet.</div> : (
              <ul>
                {learnerState.history.slice().reverse().map((item, idx) => (
                  <li key={idx}>{item.concept_id} · score {item.score.toFixed(2)} · hint {item.confidence_hint.toFixed(2)} · {item.kind}</li>
                ))}
              </ul>
            )}
          </section>

          <section className="card">
            <h2>Compliance</h2>
            <div className="compliance-grid">
              <div><strong>Sources</strong><br />{domain.compliance.sources}</div>
              <div><strong>Attribution</strong><br />{domain.compliance.attributionRequired ? "required" : "not required"}</div>
              <div><strong>Share-alike</strong><br />{domain.compliance.shareAlikeRequired ? "yes" : "no"}</div>
              <div><strong>Noncommercial</strong><br />{domain.compliance.noncommercialOnly ? "yes" : "no"}</div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
