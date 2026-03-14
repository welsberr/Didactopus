import React, { useEffect, useMemo, useState } from "react";
import { login, refresh, fetchPacks, fetchLearnerState, putLearnerState, fetchGraphAnimation } from "./api";
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

function nodeColor(status) {
  if (status === "mastered") return "#1f7a1f";
  if (status === "active") return "#2d6cdf";
  if (status === "available") return "#c48a00";
  return "#9aa4b2";
}

function GraphView({ frame }) {
  if (!frame) return null;
  const width = 760;
  const height = 420;
  const positions = {};
  frame.nodes.forEach((node, idx) => {
    positions[node.id] = { x: 120 + idx * 220, y: 120 + (idx % 2) * 150 };
  });
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="graph">
      {frame.edges.map((edge, idx) => {
        const s = positions[edge.source];
        const t = positions[edge.target];
        if (!s || !t) return null;
        return <line key={idx} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#b8c2cf" strokeWidth="3" markerEnd="url(#arrow)" />;
      })}
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#b8c2cf" />
        </marker>
      </defs>
      {frame.nodes.map((node) => {
        const p = positions[node.id];
        return (
          <g key={node.id}>
            <circle cx={p.x} cy={p.y} r={node.size} fill={nodeColor(node.status)} opacity="0.9" />
            <text x={p.x} y={p.y - 4} textAnchor="middle" className="svg-label">{node.title}</text>
            <text x={p.x} y={p.y + 14} textAnchor="middle" className="svg-small">{node.score.toFixed(2)} · {node.status}</text>
          </g>
        );
      })}
    </svg>
  );
}

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [packs, setPacks] = useState([]);
  const [learnerId] = useState("wesley-learner");
  const [packId, setPackId] = useState("");
  const [graphData, setGraphData] = useState(null);
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

  async function reload(pid) {
    const data = await guarded((token) => fetchGraphAnimation(token, learnerId, pid));
    setGraphData(data);
    setFrameIndex(0);
  }

  useEffect(() => {
    if (!auth) return;
    async function load() {
      const p = await guarded((token) => fetchPacks(token));
      setPacks(p);
      const pid = p[0]?.id || "";
      setPackId(pid);
      if (pid) await reload(pid);
    }
    load();
  }, [auth]);

  useEffect(() => {
    if (!playing || !graphData?.frames?.length) return;
    const t = setInterval(() => {
      setFrameIndex((idx) => idx >= graphData.frames.length - 1 ? 0 : idx + 1);
    }, 900);
    return () => clearInterval(t);
  }, [playing, graphData]);

  const frame = graphData?.frames?.[frameIndex];

  async function generateDemo() {
    let state = await guarded((token) => fetchLearnerState(token, learnerId));
    const now1 = new Date().toISOString();
    state.history.push({ concept_id: "intro", dimension: "mastery", score: 0.30, confidence_hint: 0.5, timestamp: now1, kind: "exercise", source_id: "demo-1" });
    state.records = [{ concept_id: "intro", dimension: "mastery", score: 0.30, confidence: 0.30, evidence_count: 1, last_updated: now1 }];
    await guarded((token) => putLearnerState(token, learnerId, state));

    const now2 = new Date(Date.now() + 1000).toISOString();
    state.history.push({ concept_id: "intro", dimension: "mastery", score: 0.78, confidence_hint: 0.7, timestamp: now2, kind: "review", source_id: "demo-2" });
    state.records = [{ concept_id: "intro", dimension: "mastery", score: 0.78, confidence: 0.70, evidence_count: 2, last_updated: now2 }];
    await guarded((token) => putLearnerState(token, learnerId, state));

    const now3 = new Date(Date.now() + 2000).toISOString();
    state.history.push({ concept_id: "second", dimension: "mastery", score: 0.42, confidence_hint: 0.5, timestamp: now3, kind: "exercise", source_id: "demo-3" });
    state.records = [
      { concept_id: "intro", dimension: "mastery", score: 0.78, confidence: 0.70, evidence_count: 2, last_updated: now2 },
      { concept_id: "second", dimension: "mastery", score: 0.42, confidence: 0.40, evidence_count: 1, last_updated: now3 }
    ];
    await guarded((token) => putLearnerState(token, learnerId, state));

    const now4 = new Date(Date.now() + 3000).toISOString();
    state.history.push({ concept_id: "second", dimension: "mastery", score: 0.72, confidence_hint: 0.7, timestamp: now4, kind: "review", source_id: "demo-4" });
    state.records = [
      { concept_id: "intro", dimension: "mastery", score: 0.78, confidence: 0.70, evidence_count: 2, last_updated: now2 },
      { concept_id: "second", dimension: "mastery", score: 0.72, confidence: 0.65, evidence_count: 2, last_updated: now4 }
    ];
    await guarded((token) => putLearnerState(token, learnerId, state));

    await reload(packId);
    setMessage("Demo graph animation frames generated.");
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus animated concept graph</h1>
          <p>Replay node-level mastery, unlocks, and prerequisite structure over time.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="controls">
          <label>Pack
            <select value={packId} onChange={async (e) => { setPackId(e.target.value); await reload(e.target.value); }}>
              {packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
          </label>
          <button onClick={() => setPlaying((x) => !x)}>{playing ? "Pause" : "Play"}</button>
          <button onClick={generateDemo}>Generate demo</button>
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <main className="layout twocol">
        <section className="card">
          <h2>Graph animation</h2>
          <div className="frame-meta">
            <div><strong>Frame:</strong> {frameIndex + 1} / {graphData?.frames?.length || 0}</div>
            <div><strong>Event:</strong> {frame?.event_kind || "-"}</div>
            <div><strong>Focus:</strong> {frame?.focus_concept_id || "-"}</div>
            <div><strong>Timestamp:</strong> {frame?.timestamp || "-"}</div>
          </div>
          <GraphView frame={frame} />
        </section>
        <section className="card">
          <h2>Graph payload</h2>
          <pre className="prebox">{JSON.stringify(graphData, null, 2)}</pre>
        </section>
      </main>
    </div>
  );
}
