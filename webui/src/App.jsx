import React, { useEffect, useState } from "react";
import { login, refresh, fetchPacks, fetchLearnerState, putLearnerState, fetchGraphAnimation, createRenderBundle } from "./api";
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

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [packs, setPacks] = useState([]);
  const [learnerId] = useState("wesley-learner");
  const [packId, setPackId] = useState("");
  const [bundle, setBundle] = useState(null);
  const [format, setFormat] = useState("gif");
  const [fps, setFps] = useState(2);
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

  useEffect(() => {
    if (!auth) return;
    async function load() {
      const p = await guarded((token) => fetchPacks(token));
      setPacks(p);
      setPackId(p[0]?.id || "");
    }
    load();
  }, [auth]);

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
    setMessage("Demo state generated.");
  }

  async function renderNow() {
    const result = await guarded((token) => createRenderBundle(token, learnerId, packId, { learner_id: learnerId, pack_id: packId, format, fps, theme: "default" }));
    setBundle(result);
    setMessage("Render bundle created.");
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus media rendering pipeline</h1>
          <p>Create GIF/MP4-ready render bundles from animated learning graphs.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="controls">
          <label>Pack
            <select value={packId} onChange={(e) => setPackId(e.target.value)}>
              {packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
          </label>
          <label>Format
            <select value={format} onChange={(e) => setFormat(e.target.value)}>
              <option value="gif">GIF</option>
              <option value="mp4">MP4</option>
            </select>
          </label>
          <label>FPS
            <input type="number" value={fps} onChange={(e) => setFps(Number(e.target.value || 2))} />
          </label>
          <button onClick={generateDemo}>Generate demo state</button>
          <button onClick={renderNow}>Create render bundle</button>
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <main className="layout twocol">
        <section className="card">
          <h2>Bundle output</h2>
          <pre className="prebox">{JSON.stringify(bundle, null, 2)}</pre>
        </section>
        <section className="card">
          <h2>What this bundle contains</h2>
          <div className="explain">
            <p>Each bundle includes SVG frames, a JSON manifest, and a render shell script suitable for FFmpeg-based conversion.</p>
            <p>This keeps artifact generation decoupled from the API server while still making render production straightforward.</p>
          </div>
        </section>
      </main>
    </div>
  );
}
