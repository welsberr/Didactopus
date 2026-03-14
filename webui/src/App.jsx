import React, { useEffect, useState } from "react";
import { login, refresh, fetchPacks, createContribution, fetchAdminPacks, fetchPackValidation, fetchPackProvenance, fetchPackVersions, fetchPackComments, fetchSubmissions, fetchSubmissionDiff, fetchSubmissionGates, fetchReviewTasks, upsertPack, publishPack, governanceAction, addReviewComment } from "./api";
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
      <button className={tab==="contribute" ? "active-tab" : ""} onClick={() => setTab("contribute")}>Contribute</button>
      {role === "admin" ? <>
        <button className={tab==="submissions" ? "active-tab" : ""} onClick={() => setTab("submissions")}>Submissions</button>
        <button className={tab==="review" ? "active-tab" : ""} onClick={() => setTab("review")}>Governance</button>
      </> : null}
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [tab, setTab] = useState("contribute");
  const [packs, setPacks] = useState([]);
  const [adminPacks, setAdminPacks] = useState([]);
  const [selectedPackId, setSelectedPackId] = useState("");
  const [validation, setValidation] = useState(null);
  const [provenance, setProvenance] = useState(null);
  const [versions, setVersions] = useState([]);
  const [comments, setComments] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [selectedSubmissionId, setSelectedSubmissionId] = useState(null);
  const [submissionDiff, setSubmissionDiff] = useState(null);
  const [submissionGates, setSubmissionGates] = useState(null);
  const [reviewTasks, setReviewTasks] = useState([]);
  const [commentText, setCommentText] = useState("Looks structurally plausible.");
  const [reviewSummary, setReviewSummary] = useState("Reviewed and ready for next stage.");
  const [message, setMessage] = useState("");
  const [contribPack, setContribPack] = useState({
    id: "bayes-pack",
    title: "Bayesian Reasoning",
    subtitle: "Contributor revision scaffold",
    level: "novice-friendly",
    concepts: [{ id: "prior", title: "Prior", prerequisites: [], masteryDimension: "mastery", exerciseReward: "Prior badge earned" }],
    onboarding: { headline: "Start here", body: "Begin", checklist: [] },
    compliance: { sources: 1, attributionRequired: true, shareAlikeRequired: false, noncommercialOnly: false, flags: [] }
  });

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
      if (auth.role === "admin") {
        setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
        setSubmissions(await guarded((token) => fetchSubmissions(token)));
        setReviewTasks(await guarded((token) => fetchReviewTasks(token)));
      }
    }
    load();
  }, [auth]);

  useEffect(() => {
    if (!auth?.role || auth.role !== "admin" || !selectedPackId) return;
    async function loadPackReview() {
      setValidation(await guarded((token) => fetchPackValidation(token, selectedPackId)));
      setProvenance(await guarded((token) => fetchPackProvenance(token, selectedPackId)));
      setVersions(await guarded((token) => fetchPackVersions(token, selectedPackId)));
      setComments(await guarded((token) => fetchPackComments(token, selectedPackId)));
    }
    loadPackReview();
  }, [auth, selectedPackId]);

  useEffect(() => {
    if (!auth?.role || auth.role !== "admin" || !selectedSubmissionId) return;
    async function loadSubmission() {
      setSubmissionDiff(await guarded((token) => fetchSubmissionDiff(token, selectedSubmissionId)));
      setSubmissionGates(await guarded((token) => fetchSubmissionGates(token, selectedSubmissionId)));
    }
    loadSubmission()
  }, [auth, selectedSubmissionId]);

  async function submitContribution() {
    const result = await guarded((token) => createContribution(token, { pack: contribPack, submission_summary: "Contributor-submitted revision from UI scaffold" }));
    setMessage(`Submission created: ${result.submission_id}`);
  }

  async function doGovernance(status) {
    await guarded((token) => governanceAction(token, selectedPackId, { status, review_summary: reviewSummary }));
    setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
    setVersions(await guarded((token) => fetchPackVersions(token, selectedPackId)));
    setMessage(`Pack moved to ${status}`);
  }

  async function addCommentNow() {
    const versionNumber = versions[0]?.version_number || 1;
    await guarded((token) => addReviewComment(token, selectedPackId, versionNumber, { comment_text: commentText, disposition: "comment" }));
    setComments(await guarded((token) => fetchPackComments(token, selectedPackId)));
    setMessage("Review comment added");
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus contribution management layer</h1>
          <p>Contributor submissions, diffs, QA/provenance gates, and reviewer task queue scaffolding.</p>
          <div className="muted">Signed in as {auth.username} ({auth.role})</div>
          {message ? <div className="message">{message}</div> : null}
        </div>
        <div className="hero-controls">
          {auth.role === "admin" ? (
            <label>Pack<select value={selectedPackId} onChange={(e) => setSelectedPackId(e.target.value)}>{adminPacks.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></label>
          ) : (
            <label>Base pack<select value={contribPack.id} onChange={(e) => setContribPack({ ...contribPack, id: e.target.value })}>{packs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></label>
          )}
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <NavTabs tab={tab} setTab={setTab} role={auth.role} />

      {tab === "contribute" && (
        <main className="layout onecol">
          <section className="card">
            <h2>Contributor submission</h2>
            <label>Pack title<input value={contribPack.title} onChange={(e) => setContribPack({ ...contribPack, title: e.target.value })} /></label>
            <label>Subtitle<input value={contribPack.subtitle} onChange={(e) => setContribPack({ ...contribPack, subtitle: e.target.value })} /></label>
            <label>Onboarding headline<input value={contribPack.onboarding.headline} onChange={(e) => setContribPack({ ...contribPack, onboarding: { ...contribPack.onboarding, headline: e.target.value } })} /></label>
            <label>Onboarding body<textarea value={contribPack.onboarding.body} onChange={(e) => setContribPack({ ...contribPack, onboarding: { ...contribPack.onboarding, body: e.target.value } })} /></label>
            <button className="primary" onClick={submitContribution}>Submit contribution</button>
            <pre className="prebox">{JSON.stringify(contribPack, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "submissions" && auth.role === "admin" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Submission queue</h2>
            <table className="table">
              <thead><tr><th>ID</th><th>Pack</th><th>Version</th><th>Status</th><th>Select</th></tr></thead>
              <tbody>
                {submissions.map((s) => (
                  <tr key={s.submission_id}>
                    <td>{s.submission_id}</td>
                    <td>{s.pack_id}</td>
                    <td>{s.proposed_version_number}</td>
                    <td>{s.status}</td>
                    <td><button onClick={() => setSelectedSubmissionId(s.submission_id)}>Inspect</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <h3>Review tasks</h3>
            <pre className="prebox">{JSON.stringify(reviewTasks, null, 2)}</pre>
          </section>
          <section className="card">
            <h2>Submission diff and gates</h2>
            <h3>Diff summary</h3>
            <pre className="prebox">{JSON.stringify(submissionDiff, null, 2)}</pre>
            <h3>Gate summary</h3>
            <pre className="prebox">{JSON.stringify(submissionGates, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "review" && auth.role === "admin" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Governance and approval gates</h2>
            <div className="button-row">
              <button onClick={() => doGovernance("in_review")}>Move to in_review</button>
              <button onClick={() => doGovernance("approved")}>Approve</button>
              <button onClick={() => doGovernance("rejected")}>Reject</button>
              <button onClick={() => publishPack(auth.access_token, selectedPackId, true)}>Publish directly</button>
            </div>
            <label>Review summary<textarea value={reviewSummary} onChange={(e) => setReviewSummary(e.target.value)} /></label>
            <h3>Validation</h3>
            <pre className="prebox">{JSON.stringify(validation, null, 2)}</pre>
            <h3>Provenance</h3>
            <pre className="prebox">{JSON.stringify(provenance, null, 2)}</pre>
          </section>
          <section className="card">
            <h2>Versions and comments</h2>
            <h3>Versions</h3>
            <pre className="prebox">{JSON.stringify(versions, null, 2)}</pre>
            <label>Reviewer comment<textarea value={commentText} onChange={(e) => setCommentText(e.target.value)} /></label>
            <button className="primary" onClick={addCommentNow}>Add comment</button>
            <h3>Comments</h3>
            <pre className="prebox">{JSON.stringify(comments, null, 2)}</pre>
          </section>
        </main>
      )}
    </div>
  );
}
