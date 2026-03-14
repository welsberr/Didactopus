import React, { useEffect, useState } from "react";
import { login, refresh, fetchDeploymentPolicy, fetchAgentCapabilities, listServiceAccounts, createServiceAccount } from "./api";
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
  const [policy, setPolicy] = useState(null);
  const [caps, setCaps] = useState(null);
  const [serviceAccounts, setServiceAccounts] = useState([]);
  const [created, setCreated] = useState(null);
  const [form, setForm] = useState({ name: "agent-learner-1", description: "AI learner account", scopes: ["packs:read","learners:read","learners:write","recommendations:read","evaluators:submit","evaluators:read"] });

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
      setPolicy(await guarded((token) => fetchDeploymentPolicy(token)));
      setCaps(await guarded((token) => fetchAgentCapabilities(token)));
      if (auth.role === "admin") {
        setServiceAccounts(await guarded((token) => listServiceAccounts(token)));
      }
    }
    load();
  }, [auth]);

  async function createNow() {
    const result = await guarded((token) => createServiceAccount(token, form));
    setCreated(result);
    setServiceAccounts(await guarded((token) => listServiceAccounts(token)));
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus agent service-account layer</h1>
          <p>First-class machine identities with scoped API access for AI learners.</p>
          <div className="muted">Signed in as {auth.username} ({auth.role})</div>
        </div>
        <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
      </header>

      <main className="layout twocol">
        <section className="card">
          <h2>Deployment policy</h2>
          <pre className="prebox">{JSON.stringify(policy, null, 2)}</pre>
          <h2>Agent capabilities</h2>
          <pre className="prebox">{JSON.stringify(caps, null, 2)}</pre>
        </section>

        <section className="card">
          <h2>Service accounts</h2>
          {auth.role === "admin" ? (
            <>
              <label>Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
              <label>Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
              <label>Scopes (comma-separated)<input value={form.scopes.join(", ")} onChange={(e) => setForm({ ...form, scopes: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} /></label>
              <button className="primary" onClick={createNow}>Create service account</button>
              <h3>Created credential</h3>
              <pre className="prebox">{JSON.stringify(created, null, 2)}</pre>
              <h3>Existing accounts</h3>
              <pre className="prebox">{JSON.stringify(serviceAccounts, null, 2)}</pre>
            </>
          ) : (
            <div className="muted">Admin required.</div>
          )}
        </section>
      </main>
    </div>
  );
}
