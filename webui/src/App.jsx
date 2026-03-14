import React, { useEffect, useMemo, useState } from "react";
import {
  login, refresh, fetchPacks, fetchAdminPacks, upsertPack, publishPack,
  createLearner, listLearners, fetchLearnerState, fetchRecommendations, postEvidence,
  submitEvaluatorJob, fetchEvaluatorHistory
} from "./api";
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
    } catch {
      setError("Login failed");
    }
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
      {role === "admin" ? <button className={tab==="admin" ? "active-tab" : ""} onClick={() => setTab("admin")}>Pack admin</button> : null}
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
  const [newLearnerId, setNewLearnerId] = useState("wesley-learner");
  const [newPackJson, setNewPackJson] = useState(JSON.stringify({
    pack: {
      id: "new-pack",
      title: "New Pack",
      subtitle: "Editable admin pack scaffold",
      level: "novice-friendly",
      concepts: [],
      onboarding: { headline: "Start here", body: "Begin", checklist: [] },
      compliance: { sources: 0, attributionRequired: false, shareAlikeRequired: false, noncommercialOnly: false, flags: [] }
    },
    is_published: false
  }, null, 2));
  const [message, setMessage] = useState("");

  async function refreshAuthToken() {
    if (!auth?.refresh_token) return null
    try {
      const result = await refresh(auth.refresh_token)
      saveAuth(result)
      setAuth(result)
      return result
    } catch {
      clearAuth()
      setAuth(null)
      return null
    }
  }

  async function guarded(fn) {
    try {
      return await fn(auth.access_token)
    } catch {
      const next = await refreshAuthToken()
      if (!next) throw new Error("auth failed")
      return await fn(next.access_token)
    }
  }

  useEffect(() => {
    if (!auth) return
    async function load() {
      const p = await guarded((token) => fetchPacks(token))
      setPacks(p)
      setSelectedPackId((prev) => prev || p[0]?.id || "")
      const ls = await guarded((token) => listLearners(token))
      setLearners(ls)
      if (ls.length === 0) {
        await guarded((token) => createLearner(token, selectedLearnerId, selectedLearnerId))
        const ls2 = await guarded((token) => listLearners(token))
        setLearners(ls2)
      }
      if (auth.role === "admin") {
        const ap = await guarded((token) => fetchAdminPacks(token))
        setAdminPacks(ap)
      }
    }
    load()
  }, [auth])

  useEffect(() => {
    if (!auth || !selectedLearnerId || !selectedPackId) return
    async function loadLearnerStuff() {
      const state = await guarded((token) => fetchLearnerState(token, selectedLearnerId))
      setLearnerState(state)
      const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId))
      setCards(recs.cards || [])
      const hist = await guarded((token) => fetchEvaluatorHistory(token, selectedLearnerId))
      setHistory(hist)
    }
    loadLearnerStuff()
  }, [auth, selectedLearnerId, selectedPackId])

  const pack = useMemo(() => packs.find((p) => p.id === selectedPackId) || null, [packs, selectedPackId])

  async function simulateCard(card) {
    await guarded((token) => postEvidence(token, selectedLearnerId, {
      concept_id: card.conceptId,
      dimension: "mastery",
      score: card.scoreHint,
      confidence_hint: card.confidenceHint,
      timestamp: new Date().toISOString(),
      kind: "checkpoint",
      source_id: `ui-${card.id}`
    }))
    const state = await guarded((token) => fetchLearnerState(token, selectedLearnerId))
    setLearnerState(state)
    const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId))
    setCards(recs.cards || [])
    setMessage(card.reward)
  }

  async function runEvaluator() {
    if (!pack?.concepts?.length) return
    await guarded((token) => submitEvaluatorJob(token, selectedLearnerId, {
      pack_id: selectedPackId,
      concept_id: pack.concepts[0].id,
      submitted_text: "This is a moderately detailed learner response intended to trigger a somewhat better prototype evaluator score.",
      kind: "checkpoint"
    }))
    setTimeout(async () => {
      const hist = await guarded((token) => fetchEvaluatorHistory(token, selectedLearnerId))
      setHistory(hist)
      const state = await guarded((token) => fetchLearnerState(token, selectedLearnerId))
      setLearnerState(state)
      const recs = await guarded((token) => fetchRecommendations(token, selectedLearnerId, selectedPackId))
      setCards(recs.cards || [])
    }, 1200)
  }

  async function createLearnerNow() {
    await guarded((token) => createLearner(token, newLearnerId, newLearnerId))
    const ls = await guarded((token) => listLearners(token))
    setLearners(ls)
    setSelectedLearnerId(newLearnerId)
  }

  async function savePack() {
    const payload = JSON.parse(newPackJson)
    await guarded((token) => upsertPack(token, payload))
    const ap = await guarded((token) => fetchAdminPacks(token))
    const p = await guarded((token) => fetchPacks(token))
    setAdminPacks(ap)
    setPacks(p)
  }

  async function togglePublish(packId, isPublished) {
    await guarded((token) => publishPack(token, packId, isPublished))
    const ap = await guarded((token) => fetchAdminPacks(token))
    const p = await guarded((token) => fetchPacks(token))
    setAdminPacks(ap)
    setPacks(p)
  }

  if (!auth) return <LoginView onAuth={setAuth} />

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus workflow scaffold</h1>
          <p>Login, refresh, learner management, evaluator history, and admin pack publication workflows.</p>
          <div className="muted">Signed in as {auth.username} ({auth.role})</div>
          {message ? <div className="message">{message}</div> : null}
        </div>
        <div className="hero-controls">
          <label>Learner<select value={selectedLearnerId} onChange={(e) => setSelectedLearnerId(e.target.value)}>
            {learners.map((l) => <option key={l.learner_id} value={l.learner_id}>{l.display_name || l.learner_id}</option>)}
          </select></label>
          <label>Pack<select value={selectedPackId} onChange={(e) => setSelectedPackId(e.target.value)}>
            {packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select></label>
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <NavTabs tab={tab} setTab={setTab} role={auth.role} />

      {tab === "learner" && (
        <main className="layout">
          <section className="card">
            <h2>Learner dashboard</h2>
            <p><strong>Pack:</strong> {pack?.title || "-"}</p>
            <p>{pack?.subtitle || ""}</p>
            <button onClick={runEvaluator}>Submit demo evaluator job</button>
            <h3>Next actions</h3>
            <div className="steps-stack">
              {cards.length ? cards.map((card) => (
                <div key={card.id} className="step-card">
                  <div className="step-header">
                    <div>
                      <h4>{card.title}</h4>
                      <div className="muted">{card.minutes} minutes</div>
                    </div>
                    <div className="reward-pill">{card.reward}</div>
                  </div>
                  <p>{card.reason}</p>
                  <details>
                    <summary>Why this is recommended</summary>
                    <ul>{card.why.map((w, idx) => <li key={idx}>{w}</li>)}</ul>
                  </details>
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
        <main className="layout onecol">
          <section className="card">
            <h2>Evaluator history</h2>
            {history.length ? (
              <table className="table">
                <thead><tr><th>Job</th><th>Status</th><th>Concept</th><th>Score</th><th>Confidence</th><th>Notes</th></tr></thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.job_id}>
                      <td>{row.job_id}</td>
                      <td>{row.status}</td>
                      <td>{row.concept_id}</td>
                      <td>{row.result_score ?? "-"}</td>
                      <td>{row.result_confidence_hint ?? "-"}</td>
                      <td>{row.result_notes || ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="muted">No evaluator jobs yet.</div>}
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
            <h2>Pack editor</h2>
            <textarea className="bigtext" value={newPackJson} onChange={(e) => setNewPackJson(e.target.value)} />
            <button className="primary" onClick={savePack}>Save pack</button>
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
    </div>
  )
}
