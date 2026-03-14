import React, { useEffect, useState } from "react";
import { login, refresh, fetchPacks, fetchAdminPacks, fetchPackValidation, fetchPackProvenance, upsertPack, publishPack, listLearners, createLearner, fetchLearnerState, fetchRecommendations, postEvidence, submitEvaluatorJob, fetchEvaluatorHistory, fetchEvaluatorTrace } from "./api";
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

function NavTabs({ tab, setTab, role }) {
  return (
    <div className="tab-row">
      <button className={tab==="learner" ? "active-tab" : ""} onClick={() => setTab("learner")}>Learner</button>
      <button className={tab==="history" ? "active-tab" : ""} onClick={() => setTab("history")}>Evaluator history</button>
      <button className={tab==="manage" ? "active-tab" : ""} onClick={() => setTab("manage")}>Learners</button>
      {role === "admin" ? <>
        <button className={tab==="admin" ? "active-tab" : ""} onClick={() => setTab("admin")}>Pack admin</button>
        <button className={tab==="review" ? "active-tab" : ""} onClick={() => setTab("review")}>Curation review</button>
      </> : null}
    </div>
  );
}

function PackAuthorForm({ value, onChange, onSave }) {
  function setField(field, val) { onChange({ ...value, [field]: val }); }
  function setCompliance(field, val) { onChange({ ...value, compliance: { ...value.compliance, [field]: val } }); }
  return (
    <div className="form-grid">
      <label>Pack ID<input value={value.id} onChange={(e) => setField("id", e.target.value)} /></label>
      <label>Title<input value={value.title} onChange={(e) => setField("title", e.target.value)} /></label>
      <label className="full">Subtitle<input value={value.subtitle} onChange={(e) => setField("subtitle", e.target.value)} /></label>
      <label>Level<input value={value.level} onChange={(e) => setField("level", e.target.value)} /></label>
      <label>Source count<input type="number" value={value.compliance.sources} onChange={(e) => setCompliance("sources", Number(e.target.value))} /></label>
      <label className="full">Onboarding headline<input value={value.onboarding.headline} onChange={(e) => onChange({ ...value, onboarding: { ...value.onboarding, headline: e.target.value } })} /></label>
      <label className="full">Onboarding body<textarea value={value.onboarding.body} onChange={(e) => onChange({ ...value, onboarding: { ...value.onboarding, body: e.target.value } })} /></label>
      <div className="checkrow full">
        <label><input type="checkbox" checked={value.compliance.attributionRequired} onChange={(e) => setCompliance("attributionRequired", e.target.checked)} /> Attribution required</label>
        <label><input type="checkbox" checked={value.compliance.shareAlikeRequired} onChange={(e) => setCompliance("shareAlikeRequired", e.target.checked)} /> Share-alike</label>
        <label><input type="checkbox" checked={value.compliance.noncommercialOnly} onChange={(e) => setCompliance("noncommercialOnly", e.target.checked)} /> Noncommercial only</label>
      </div>
      <div className="full"><button className="primary" onClick={onSave}>Save pack</button></div>
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [tab, setTab] = useState("learner");
  const [packs, setPacks] = useState([]);
  const [adminPacks, setAdminPacks] = useState([]);
  const [learners, setLearners] = useState([]);
  const [selectedLearnerId, setSelectedLearnerId] = useState("wesley-learner");
  const [selectedPackId, setSelectedPackId] = useState("");
  const [learnerState, setLearnerState] = useState(null);
  const [cards, setCards] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [validation, setValidation] = useState(null);
  const [provenance, setProvenance] = useState(null);
  const [newLearnerId, setNewLearnerId] = useState("wesley-learner");
  const [formPack, setFormPack] = useState({ id: "new-pack", title: "New Pack", subtitle: "Editable admin pack scaffold", level: "novice-friendly", concepts: [], onboarding: { headline: "Start here", body: "Begin", checklist: [] }, compliance: { sources: 0, attributionRequired: false, shareAlikeRequired: false, noncommercialOnly: false, flags: [] } });
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
      setSelectedPackId((prev) => prev || p[0]?.id || "");
      let ls = await guarded((token) => listLearners(token));
      if (ls.length === 0) {
        await guarded((token) => createLearner(token, selectedLearnerId, selectedLearnerId));
        ls = await guarded((token) => listLearners(token));
      }
      setLearners(ls);
      if (auth.role === "admin") {
        const ap = await guarded((token) => fetchAdminPacks(token));
        setAdminPacks(ap);
      }
    }
    load();
  }, [auth]);

  useEffect(() => {
    if (!auth || !selectedLearnerId || !selectedPackId) return;
    async function loadLearnerStuff() {
      setLearnerState(await guarded((token) => fetchLearnerState(token, selectedLearnerId)));
      const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId));
      setCards(recs.cards || []);
      setHistory(await guarded((token) => fetchEvaluatorHistory(token, selectedLearnerId)));
      if (auth.role === "admin") {
        setValidation(await guarded((token) => fetchPackValidation(token, selectedPackId)));
        setProvenance(await guarded((token) => fetchPackProvenance(token, selectedPackId)));
      }
    }
    loadLearnerStuff();
  }, [auth, selectedLearnerId, selectedPackId]);

  async function simulateCard(card) {
    await guarded((token) => postEvidence(token, selectedLearnerId, { concept_id: card.conceptId, dimension: "mastery", score: card.scoreHint, confidence_hint: card.confidenceHint, timestamp: new Date().toISOString(), kind: "checkpoint", source_id: `ui-${card.id}` }));
    setLearnerState(await guarded((token) => fetchLearnerState(token, selectedLearnerId)));
    const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId));
    setCards(recs.cards || []);
    setMessage(card.reward);
  }

  async function runEvaluator() {
    const conceptId = packs.find((p) => p.id === selectedPackId)?.concepts?.[0]?.id || "prior";
    await guarded((token) => submitEvaluatorJob(token, selectedLearnerId, { pack_id: selectedPackId, concept_id: conceptId, submitted_text: "This is a moderately detailed learner response intended to trigger a somewhat better prototype evaluator score.", kind: "checkpoint" }));
    setTimeout(async () => {
      setHistory(await guarded((token) => fetchEvaluatorHistory(token, selectedLearnerId)));
      setLearnerState(await guarded((token) => fetchLearnerState(token, selectedLearnerId)));
      const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId));
      setCards(recs.cards || []);
    }, 1200);
  }

  async function createLearnerNow() {
    await guarded((token) => createLearner(token, newLearnerId, newLearnerId));
    const ls = await guarded((token) => listLearners(token));
    setLearners(ls);
    setSelectedLearnerId(newLearnerId);
  }

  async function savePack() {
    await guarded((token) => upsertPack(token, { pack: formPack, is_published: false }));
    setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
    setPacks(await guarded((token) => fetchPacks(token)));
    setMessage("Pack saved");
  }

  async function togglePublish(packId, isPublished) {
    await guarded((token) => publishPack(token, packId, isPublished));
    setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
    setPacks(await guarded((token) => fetchPacks(token)));
  }

  async function loadTrace(jobId) {
    setSelectedTrace(await guarded((token) => fetchEvaluatorTrace(token, jobId)));
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus admin curation layer</h1>
          <p>Pack validation review, provenance inspection, evaluator traces, and form-driven pack authoring.</p>
          <div className="muted">Signed in as {auth.username} ({auth.role})</div>
          {message ? <div className="message">{message}</div> : null}
        </div>
        <div className="hero-controls">
          <label>Learner<select value={selectedLearnerId} onChange={(e) => setSelectedLearnerId(e.target.value)}>{learners.map((l) => <option key={l.learner_id} value={l.learner_id}>{l.display_name || l.learner_id}</option>)}</select></label>
          <label>Pack<select value={selectedPackId} onChange={(e) => setSelectedPackId(e.target.value)}>{packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></label>
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <NavTabs tab={tab} setTab={setTab} role={auth.role} />

      {tab === "learner" && (
        <main className="layout onecol">
          <section className="card">
            <h2>Learner dashboard</h2>
            <button onClick={runEvaluator}>Submit demo evaluator job</button>
            <div className="steps-stack">
              {cards.length ? cards.map((card) => (
                <div key={card.id} className="step-card">
                  <div className="step-header">
                    <div><h4>{card.title}</h4><div className="muted">{card.minutes} minutes</div></div>
                    <div className="reward-pill">{card.reward}</div>
                  </div>
                  <p>{card.reason}</p>
                  <details><summary>Why this is recommended</summary><ul>{card.why.map((w, idx) => <li key={idx}>{w}</li>)}</ul></details>
                  <button className="primary" onClick={() => simulateCard(card)}>Simulate step</button>
                </div>
              )) : <div className="muted">No recommendations available.</div>}
            </div>
            <h3>Learner state snapshot</h3>
            <pre className="prebox">{JSON.stringify(learnerState, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "history" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Evaluator history</h2>
            {history.length ? (
              <table className="table">
                <thead><tr><th>Job</th><th>Status</th><th>Concept</th><th>Score</th><th>Trace</th></tr></thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.job_id}>
                      <td>{row.job_id}</td>
                      <td>{row.status}</td>
                      <td>{row.concept_id}</td>
                      <td>{row.result_score ?? "-"}</td>
                      <td><button onClick={() => loadTrace(row.job_id)}>Inspect trace</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="muted">No evaluator jobs yet.</div>}
          </section>
          <section className="card">
            <h2>Evaluator trace</h2>
            <pre className="prebox">{JSON.stringify(selectedTrace, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "manage" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Learner management</h2>
            <label>New learner ID<input value={newLearnerId} onChange={(e) => setNewLearnerId(e.target.value)} /></label>
            <button className="primary" onClick={createLearnerNow}>Create learner</button>
          </section>
          <section className="card">
            <h2>Existing learners</h2>
            <table className="table">
              <thead><tr><th>Learner ID</th><th>Display name</th><th>Owner</th></tr></thead>
              <tbody>
                {learners.map((row) => (
                  <tr key={row.learner_id}>
                    <td>{row.learner_id}</td>
                    <td>{row.display_name}</td>
                    <td>{row.owner_user_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </main>
      )}

      {tab === "admin" && auth.role === "admin" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Richer pack authoring</h2>
            <PackAuthorForm value={formPack} onChange={setFormPack} onSave={savePack} />
          </section>
          <section className="card">
            <h2>Pack administration</h2>
            <table className="table">
              <thead><tr><th>ID</th><th>Title</th><th>Published</th><th>Action</th></tr></thead>
              <tbody>
                {adminPacks.map((row) => (
                  <tr key={row.id}>
                    <td>{row.id}</td>
                    <td>{row.title}</td>
                    <td>{String(row.is_published)}</td>
                    <td><button onClick={() => togglePublish(row.id, !row.is_published)}>{row.is_published ? "Unpublish" : "Publish"}</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </main>
      )}

      {tab === "review" && auth.role === "admin" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Pack validation review</h2>
            <pre className="prebox">{JSON.stringify(validation, null, 2)}</pre>
          </section>
          <section className="card">
            <h2>Attribution / provenance inspection</h2>
            <pre className="prebox">{JSON.stringify(provenance, null, 2)}</pre>
          </section>
        </main>
      )}
    </div>
  );
}
