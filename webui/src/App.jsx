import React, { useEffect, useState } from "react";
import { login, refresh, fetchPacks, upsertPack, createContribution, fetchAdminPacks, fetchPackValidation, fetchPackProvenance, fetchPackVersions, fetchPackComments, fetchSubmissions, fetchSubmissionDiff, fetchSubmissionGates, fetchReviewTasks, publishPack, fetchPublishability, governanceAction, addReviewComment } from "./api";
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
      <button className={tab==="personal" ? "active-tab" : ""} onClick={() => setTab("personal")}>Personal packs</button>
      <button className={tab==="contribute" ? "active-tab" : ""} onClick={() => setTab("contribute")}>Community contribution</button>
      {role === "admin" ? <>
        <button className={tab==="submissions" ? "active-tab" : ""} onClick={() => setTab("submissions")}>Submissions</button>
        <button className={tab==="review" ? "active-tab" : ""} onClick={() => setTab("review")}>Governance</button>
      </> : null}
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(loadAuth());
  const [tab, setTab] = useState("personal");
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
  const [publishability, setPublishability] = useState(null);
  const [reviewTasks, setReviewTasks] = useState([]);
  const [commentText, setCommentText] = useState("Looks structurally plausible.");
  const [reviewSummary, setReviewSummary] = useState("Reviewed and ready for next stage.");
  const [message, setMessage] = useState("");
  const [personalPack, setPersonalPack] = useState({
    id: "my-private-pack",
    title: "My Private Pack",
    subtitle: "Personal lane scaffold",
    level: "novice-friendly",
    concepts: [{ id: "intro", title: "Intro", prerequisites: [], masteryDimension: "mastery", exerciseReward: "Intro" }],
    onboarding: { headline: "Start privately", body: "Personal pack lane", checklist: [] },
    compliance: { sources: 0, attributionRequired: false, shareAlikeRequired: false, noncommercialOnly: false, flags: [] }
  });
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
    async function loadReview() {
      setValidation(await guarded((token) => fetchPackValidation(token, selectedPackId)));
      setProvenance(await guarded((token) => fetchPackProvenance(token, selectedPackId)));
      setVersions(await guarded((token) => fetchPackVersions(token, selectedPackId)));
      setComments(await guarded((token) => fetchPackComments(token, selectedPackId)));
      setPublishability(await guarded((token) => fetchPublishability(token, selectedPackId)));
    }
    loadReview();
  }, [auth, selectedPackId]);

  useEffect(() => {
    if (!auth?.role || auth.role !== "admin" || !selectedSubmissionId) return;
    async function loadSubmission() {
      setSubmissionDiff(await guarded((token) => fetchSubmissionDiff(token, selectedSubmissionId)));
      setSubmissionGates(await guarded((token) => fetchSubmissionGates(token, selectedSubmissionId)));
    }
    loadSubmission();
  }, [auth, selectedSubmissionId]);

  async function savePersonalPack() {
    const result = await guarded((token) => upsertPack(token, { pack: personalPack, policy_lane: "personal", is_published: true, change_summary: "Saved through personal lane UI" }));
    setMessage(`Personal pack saved: ${result.pack_id}`);
    setPacks(await guarded((token) => fetchPacks(token)));
  }

  async function submitContribution() {
    const result = await guarded((token) => createContribution(token, { pack: contribPack, submission_summary: "Contributor-submitted revision from UI scaffold" }));
    setMessage(`Community submission created: ${result.submission_id}`);
  }

  async function doGovernance(status) {
    await guarded((token) => governanceAction(token, selectedPackId, { status, review_summary: reviewSummary }));
    setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
    setVersions(await guarded((token) => fetchPackVersions(token, selectedPackId)));
    setPublishability(await guarded((token) => fetchPublishability(token, selectedPackId)));
    setMessage(`Pack moved to ${status}`);
  }

  async function addCommentNow() {
    const versionNumber = versions[0]?.version_number || 1;
    await guarded((token) => addReviewComment(token, selectedPackId, versionNumber, { comment_text: commentText, disposition: "comment" }));
    setComments(await guarded((token) => fetchPackComments(token, selectedPackId)));
    setMessage("Review comment added");
  }

  async function publishSelected() {
    const result = await guarded((token) => publishPack(token, selectedPackId, true));
    setMessage(result.reason || "Publish updated");
    setAdminPacks(await guarded((token) => fetchAdminPacks(token)));
    setPublishability(await guarded((token) => fetchPublishability(token, selectedPackId)));
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus dual-lane policy layer</h1>
          <p>Personal packs stay low-friction. Community packs keep gates, review, and approval workflows.</p>
          <div className="muted">Signed in as {auth.username} ({auth.role})</div>
          {message ? <div className="message">{message}</div> : null}
        </div>
        <div className="hero-controls">
          {auth.role === "admin" ? (
            <label>Pack<select value={selectedPackId} onChange={(e) => setSelectedPackId(e.target.value)}>{adminPacks.map((p) => <option key={p.id} value={p.id}>{p.title} [{p.policy_lane}]</option>)}</select></label>
          ) : null}
          <button onClick={() => { clearAuth(); setAuth(null); }}>Logout</button>
        </div>
      </header>

      <NavTabs tab={tab} setTab={setTab} role={auth.role} />

      {tab === "personal" && (
        <main className="layout onecol">
          <section className="card">
            <h2>Personal lane authoring</h2>
            <p className="muted">This lane is intended not to hamper an individual building packs for private use.</p>
            <label>Pack ID<input value={personalPack.id} onChange={(e) => setPersonalPack({ ...personalPack, id: e.target.value })} /></label>
            <label>Title<input value={personalPack.title} onChange={(e) => setPersonalPack({ ...personalPack, title: e.target.value })} /></label>
            <label>Subtitle<input value={personalPack.subtitle} onChange={(e) => setPersonalPack({ ...personalPack, subtitle: e.target.value })} /></label>
            <button className="primary" onClick={savePersonalPack}>Save personal pack directly</button>
            <pre className="prebox">{JSON.stringify(personalPack, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "contribute" && (
        <main className="layout onecol">
          <section className="card">
            <h2>Community contribution lane</h2>
            <p className="muted">Use this lane for packs intended to enter shared review and publication workflows.</p>
            <label>Pack ID<input value={contribPack.id} onChange={(e) => setContribPack({ ...contribPack, id: e.target.value })} /></label>
            <label>Title<input value={contribPack.title} onChange={(e) => setContribPack({ ...contribPack, title: e.target.value })} /></label>
            <label>Subtitle<input value={contribPack.subtitle} onChange={(e) => setContribPack({ ...contribPack, subtitle: e.target.value })} /></label>
            <button className="primary" onClick={submitContribution}>Submit for community review</button>
            <pre className="prebox">{JSON.stringify(contribPack, null, 2)}</pre>
          </section>
        </main>
      )}

      {tab === "submissions" && auth.role === "admin" && (
        <main className="layout twocol">
          <section className="card">
            <h2>Submission queue</h2>
            <table className="table">
              <thead><tr><th>ID</th><th>Pack</th><th>Lane</th><th>Version</th><th>Status</th><th>Select</th></tr></thead>
              <tbody>
                {submissions.map((s) => (
                  <tr key={s.submission_id}>
                    <td>{s.submission_id}</td>
                    <td>{s.pack_id}</td>
                    <td>{s.policy_lane}</td>
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
            <h2>Governance and publishability</h2>
            <div className="button-row">
              <button onClick={() => doGovernance("in_review")}>Move to in_review</button>
              <button onClick={() => doGovernance("approved")}>Approve</button>
              <button onClick={() => doGovernance("rejected")}>Reject</button>
              <button onClick={publishSelected}>Publish</button>
            </div>
            <label>Review summary<textarea value={reviewSummary} onChange={(e) => setReviewSummary(e.target.value)} /></label>
            <h3>Publishability</h3>
            <pre className="prebox">{JSON.stringify(publishability, null, 2)}</pre>
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
