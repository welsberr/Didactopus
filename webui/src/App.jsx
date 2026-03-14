import React, { useEffect, useState } from "react";
import { login, listCandidates, createCandidate, createReview, promoteCandidate, runSynthesis, listSynthesisCandidates, promoteSynthesis } from "./api";

function LoginView({ onAuth }) {
  const [username, setUsername] = useState("reviewer");
  const [password, setPassword] = useState("demo-pass");
  const [error, setError] = useState("");
  async function doLogin() {
    try {
      const result = await login(username, password);
      onAuth(result);
    } catch {
      setError("Login failed");
    }
  }
  return (
    <div className="page narrow">
      <section className="card">
        <h1>Didactopus review workbench</h1>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button className="primary" onClick={doLogin}>Login</button>
        {error ? <div className="error">{error}</div> : null}
      </section>
    </div>
  );
}

function CandidateCard({ candidate, onReview, onPromote }) {
  return (
    <div className="card small">
      <h3>{candidate.title}</h3>
      <div className="muted">{candidate.candidate_kind} · lane: {candidate.triage_lane} · status: {candidate.current_status}</div>
      <p>{candidate.summary}</p>
      <div className="tiny">confidence {candidate.confidence_hint.toFixed(2)} · novelty {candidate.novelty_score.toFixed(2)} · synthesis {candidate.synthesis_score.toFixed(2)}</div>
      <div className="actions">
        <button onClick={() => onReview(candidate.candidate_id, "accept_pack_improvement")}>Accept as pack improvement</button>
        <button onClick={() => onPromote(candidate.candidate_id, "curriculum_draft")}>Promote to curriculum draft</button>
        <button onClick={() => onPromote(candidate.candidate_id, "reusable_skill_bundle")}>Promote to skill bundle</button>
        <button onClick={() => onPromote(candidate.candidate_id, "archive")}>Archive</button>
      </div>
    </div>
  );
}

function SynthesisCard({ item, onPromote }) {
  return (
    <div className="card small">
      <h3>{item.source_concept_id} ↔ {item.target_concept_id}</h3>
      <div className="muted">{item.source_pack_id} → {item.target_pack_id}</div>
      <p>{item.explanation}</p>
      <div className="tiny">total {item.score_total.toFixed(2)} · semantic {item.score_semantic.toFixed(2)} · structural {item.score_structural.toFixed(2)}</div>
      <button onClick={() => onPromote(item.synthesis_id)}>Promote into workflow</button>
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [synthesis, setSynthesis] = useState([]);
  const [message, setMessage] = useState("");

  async function reload(token = auth?.access_token) {
    if (!token) return;
    setCandidates(await listCandidates(token));
    setSynthesis(await listSynthesisCandidates(token));
  }

  useEffect(() => {
    if (auth?.access_token) {
      reload(auth.access_token);
    }
  }, [auth]);

  async function seedCandidate() {
    const payload = {
      source_type: "learner_export",
      source_artifact_id: null,
      learner_id: "wesley-learner",
      pack_id: "biology-pack",
      candidate_kind: "hidden_prerequisite",
      title: "Possible hidden prerequisite for drift",
      summary: "Learner evidence suggests probability intuition should be explicit before drift.",
      structured_payload: { affected_concept: "drift", suggested_prereq: "variation" },
      evidence_summary: "Repeated confusion on stochastic interpretation.",
      confidence_hint: 0.73,
      novelty_score: 0.66,
      synthesis_score: 0.42,
      triage_lane: "pack_improvement"
    };
    await createCandidate(auth.access_token, payload);
    await reload();
    setMessage("Seed candidate created.");
  }

  async function handleReview(candidateId, verdict) {
    await createReview(auth.access_token, candidateId, {
      review_kind: "human_review",
      verdict,
      rationale: "Accepted in reviewer workbench demo.",
      requested_changes: ""
    });
    await reload();
    setMessage(`Review added to candidate ${candidateId}.`);
  }

  async function handlePromote(candidateId, target) {
    await promoteCandidate(auth.access_token, candidateId, {
      promotion_target: target,
      target_object_id: "",
      promotion_status: "approved"
    });
    await reload();
    setMessage(`Candidate ${candidateId} promoted to ${target}.`);
  }

  async function handleRunSynthesis() {
    await runSynthesis(auth.access_token, { source_pack_id: "biology-pack", target_pack_id: "math-pack", limit: 12 });
    await reload();
    setMessage("Synthesis run completed.");
  }

  async function handlePromoteSynthesis(synthesisId) {
    await promoteSynthesis(auth.access_token, synthesisId, { promotion_target: "pack_improvement" });
    await reload();
    setMessage(`Synthesis candidate ${synthesisId} promoted into workflow.`);
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Review workbench + synthesis engine</h1>
          <p>Triages learner-derived knowledge into pack improvements, curriculum drafts, skill bundles, or archive, while surfacing cross-pack synthesis proposals.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="toolbar">
          <button onClick={seedCandidate}>Seed candidate</button>
          <button onClick={handleRunSynthesis}>Run synthesis</button>
          <button onClick={() => reload()}>Refresh</button>
        </div>
      </header>

      <main className="grid">
        <section>
          <h2>Knowledge candidates</h2>
          <div className="stack">
            {candidates.map((c) => (
              <CandidateCard key={c.candidate_id} candidate={c} onReview={handleReview} onPromote={handlePromote} />
            ))}
          </div>
        </section>
        <section>
          <h2>Synthesis candidates</h2>
          <div className="stack">
            {synthesis.map((s) => (
              <SynthesisCard key={s.synthesis_id} item={s} onPromote={handlePromoteSynthesis} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
