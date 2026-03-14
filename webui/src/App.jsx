import React, { useEffect, useMemo, useState } from "react";
import { login, refresh, fetchPacks, fetchLearnerState, putLearnerState, createLearnerRun, addWorkflowEvent, fetchAnimation } from "./api";
import { loadAuth, saveAuth, clearAuth } from "./authStore";

function LoginView({ onAuth }) {
  const [username, setUsername] = useState("wesley");
  const [password, setPassword] = useState("demo-pass");
  const [error, setError] = useState("");
  async function doLogin() {
    try {
      const result = await login(username, password);
      saveAuth(result);
      onAuth(result);
    } catch { setError("Login failed"); }
  }
  return (
    <div className="page narrow-page">
      <section className="card narrow">
        <h1>Didactopus login</h1>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button className="primary" onClick={doLogin}>Login</button>
        {error ? <div className="error">{error}</div> : null}
      </section>
    </div>
  );
}

function AnimationBars({ frame, concepts }) {
  if (!frame) return null;
  return (
    <div className="bars">
      {concepts.map((concept) => {
        const value = frame.scores?.[concept] ?? 0;
        return (
          <div className="bar-row" key={concept}>
            <div className="bar-label">{concept}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${Math.max(0, Math.min(100, value * 100))}%` }} />
            </div>
            <div className="bar-value">{value.toFixed(2)}</div>
          </div>
        );
      })}
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [packs, setPacks] = useState([]);
  const [learnerId] = useState("wesley-learner");
  const [packId, setPackId] = useState("");
  const [animation, setAnimation] = useState(null);
  const [frameIndex, setFrameIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [message, setMessage] = useState("");

  async function refreshAuthToken() {
    if (!auth?.refresh_token) return null;
    try {
      const result = await refresh(auth.refresh_token);
      saveAuth(result);
      setAuth(result);
      return result;
    } catch {
      clearAuth();
      setAuth(null);
      return null;
    }
  }

  async function guarded(fn) {
    try { return await fn(auth.access_token); }
    catch {
      const next = await refreshAuthToken();
      if (!next) throw new Error("auth failed");
      return await fn(next.access_token);
    }
  }

  async function reloadAnimation(pid) {
    const data = await guarded((token) => fetchAnimation(token, learnerId, pid));
    setAnimation(data);
    setFrameIndex(0);
  }

  useEffect(() => {
    if (!auth) return;
    async function load() {
      const p = await guarded((token) => fetchPacks(token));
      setPacks(p);
      const pid = p[0]?.id || "";
      setPackId(pid);
      if (pid) await reloadAnimation(pid);
    }
    load();
  }, [auth]);

  useEffect(() => {
    if (!playing || !animation?.frames?.length) return;
    const t = setInterval(() => {
      setFrameIndex((idx) => {
        if (idx >= animation.frames.length - 1) {
          return 0;
        }
        return idx + 1;
      });
    }, 900);
    return () => clearInterval(t);
  }, [playing, animation]);

  const currentFrame = animation?.frames?.[frameIndex];
  const concepts = useMemo(() => animation?.concepts || [], [animation]);

  async function simulateLearning() {
    const run = await guarded((token) => createLearnerRun(token, { learner_id: learnerId, pack_id: packId, title: "Demo animation run", actor_kind: "human" }));
    let state = await guarded((token) => fetchLearnerState(token, learnerId));
    const now1 = new Date().toISOString();
    state.history.push({ concept_id: "intro", dimension: "mastery", score: 0.35, confidence_hint: 0.5, timestamp: now1, kind: "exercise", source_id: "demo-1" });
    state.records = [{ concept_id: "intro", dimension: "mastery", score: 0.35, confidence: 0.35, evidence_count: 1, last_updated: now1 }];
    await guarded((token) => putLearnerState(token, learnerId, state));
    await guarded((token) => addWorkflowEvent(token, { run_id: run.run_id, learner_id: learnerId, event_type: "exercise_completed", concept_id: "intro", timestamp: now1, detail: { score: 0.35 } }));

    const now2 = new Date(Date.now() + 1000).toISOString();
    state.history.push({ concept_id: "intro", dimension: "mastery", score: 0.75, confidence_hint: 0.7, timestamp: now2, kind: "review", source_id: "demo-2" });
    state.records = [{ concept_id: "intro", dimension: "mastery", score: 0.75, confidence: 0.68, evidence_count: 2, last_updated: now2 }];
    await guarded((token) => putLearnerState(token, learnerId, state));
    await guarded((token) => addWorkflowEvent(token, { run_id: run.run_id, learner_id: learnerId, event_type: "review_completed", concept_id: "intro", timestamp: now2, detail: { score: 0.75 } }));

    const now3 = new Date(Date.now() + 2000).toISOString();
    state.history.push({ concept_id: "second", dimension: "mastery", score: 0.45, confidence_hint: 0.5, timestamp: now3, kind: "exercise", source_id: "demo-3" });
    state.records = [
      { concept_id: "intro", dimension: "mastery", score: 0.75, confidence: 0.68, evidence_count: 2, last_updated: now2 },
      { concept_id: "second", dimension: "mastery", score: 0.45, confidence: 0.40, evidence_count: 1, last_updated: now3 },
    ];
    await guarded((token) => putLearnerState(token, learnerId, state));
    await guarded((token) => addWorkflowEvent(token, { run_id: run.run_id, learner_id: learnerId, event_type: "unlock_progress", concept_id: "second", timestamp: now3, detail: { score: 0.45 } }));

    await reloadAnimation(packId);
    setMessage(`Demo run ${run.run_id} generated animation frames.`);
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus learning animation</h1>
          <p>Replay mastery changes for human or AI learners over time.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="controls">
          <label>Pack
            <select value={packId} onChange={async (e) => { setPackId(e.target.value); await reloadAnimation(e.target.value); }}>
              {packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
          </label>
          <button onClick={() => setPlaying((x) => !x)}>{playing ? "Pause" : "Play"}</button>
          <button onClick={simulateLearning}>Generate demo run</button>
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <main className="layout twocol">
        <section className="card">
          <h2>Current frame</h2>
          <div className="frame-meta">
            <div><strong>Frame:</strong> {frameIndex + 1} / {animation?.frames?.length || 0}</div>
            <div><strong>Event:</strong> {currentFrame?.event_kind || "-"}</div>
            <div><strong>Concept:</strong> {currentFrame?.concept_id || "-"}</div>
            <div><strong>Timestamp:</strong> {currentFrame?.timestamp || "-"}</div>
          </div>
          <AnimationBars frame={currentFrame} concepts={concepts} />
        </section>

        <section className="card">
          <h2>Animation data</h2>
          <pre className="prebox">{JSON.stringify(animation, null, 2)}</pre>
        </section>
      </main>
    </div>
  );
}
