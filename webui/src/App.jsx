import React, { useEffect, useState } from "react";
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
  return (
    <svg viewBox="0 0 960 560" className="graph">
      {frame.edges.map((edge, idx) => {
        const s = frame.nodes.find((n) => n.id === edge.source);
        const t = frame.nodes.find((n) => n.id === edge.target);
        if (!s || !t) return null;
        return <line key={idx} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#b8c2cf" strokeWidth="3" markerEnd="url(#arrow)" />;
      })}
      {frame.cross_pack_links.map((edge, idx) => {
        const s = frame.nodes.find((n) => n.id === edge.source);
        if (!s) return null;
        return <line key={`c${idx}`} x1={s.x} y1={s.y} x2={s.x + 120} y2={s.y - 60} stroke="#cc4bc2" strokeWidth="2" strokeDasharray="8 6" />;
      })}
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#b8c2cf" />
        </marker>
      </defs>
      {frame.nodes.map((node) => (
        <g key={node.id}>
          <circle cx={node.x} cy={node.y} r={node.size} fill={nodeColor(node.status)} opacity="0.92" />
          <text x={node.x} y={node.y - 4} textAnchor="middle" className="svg-label">{node.title}</text>
          <text x={node.x} y={node.y + 14} textAnchor="middle" className="svg-small">{node.score.toFixed(2)} · {node.status}</text>
        </g>
      ))}
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

  async function generateDemo() {
    let state = await guarded((token) => fetchLearnerState(token, learnerId));
    const base = Date.now();
    const events = [
      ["intro", 0.30, "exercise", 0],
      ["intro", 0.78, "review", 1000],
      ["second", 0.42, "exercise", 2000],
      ["second", 0.72, "review", 3000],
      ["third", 0.25, "exercise", 4000],
      ["branch", 0.60, "exercise", 5000],
    ];
    const latest = {}
    for (const [cid, score, kind, offset] of events) {
      const ts = new Date(base + offset).toISOString();
      state.history.push({ concept_id: cid, dimension: "mastery", score, confidence_hint: 0.6, timestamp: ts, kind, source_id: `demo-${cid}-${offset}` });
      latest[cid] = { concept_id: cid, dimension: "mastery", score, confidence: Math.min(0.9, score), evidence_count: (latest[cid]?.evidence_count || 0) + 1, last_updated: ts };
    }
    state.records = Object.values(latest);
    await guarded((token) => putLearnerState(token, learnerId, state));
    await reload(packId);
    setMessage("Stable-layout graph demo generated.");
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  const frame = graphData?.frames?.[frameIndex];

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus layout-aware graph engine</h1>
          <p>Stable node positions, cross-pack links, and export-ready graph frames.</p>
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
          <h2>Frame payload</h2>
          <pre className="prebox">{JSON.stringify(graphData, null, 2)}</pre>
        </section>
      </main>
    </div>
  );
}
