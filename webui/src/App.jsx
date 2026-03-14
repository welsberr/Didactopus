import React, { useEffect, useState } from "react";
import { login, listCandidates, createCandidate, promoteCandidate, runSynthesis, listSynthesisCandidates, promoteSynthesis, listPackPatches, listCurriculumDrafts, listSkillBundles } from "./api";

function LoginView({ onAuth }) {
  const [username, setUsername] = useState("reviewer");
  const [password, setPassword] = useState("demo-pass");
  const [error, setError] = useState("");
  async function doLogin() {
    try { onAuth(await login(username, password)); }
    catch { setError("Login failed"); }
  }
  return (
    <div className="page narrow"><section className="card">
      <h1>Didactopus promotion targets</h1>
      <label>Username<input value={username} onChange={(e)=>setUsername(e.target.value)} /></label>
      <label>Password<input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} /></label>
      <button className="primary" onClick={doLogin}>Login</button>
      {error ? <div className="error">{error}</div> : null}
    </section></div>
  );
}

function CandidateCard({ candidate, onPromote }) {
  return (
    <div className="card small">
      <h3>{candidate.title}</h3>
      <div className="muted">{candidate.candidate_kind} · {candidate.triage_lane}</div>
      <p>{candidate.summary}</p>
      <div className="actions">
        <button onClick={() => onPromote(candidate.candidate_id, "pack_improvement")}>Make patch proposal</button>
        <button onClick={() => onPromote(candidate.candidate_id, "curriculum_draft")}>Make curriculum draft</button>
        <button onClick={() => onPromote(candidate.candidate_id, "reusable_skill_bundle")}>Make skill bundle</button>
        <button onClick={() => onPromote(candidate.candidate_id, "archive")}>Archive</button>
      </div>
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [synthesis, setSynthesis] = useState([]);
  const [patches, setPatches] = useState([]);
  const [curriculum, setCurriculum] = useState([]);
  const [skills, setSkills] = useState([]);
  const [message, setMessage] = useState("");

  async function reload(token = auth?.access_token) {
    if (!token) return;
    const [c, s, p, d, k] = await Promise.all([
      listCandidates(token),
      listSynthesisCandidates(token),
      listPackPatches(token),
      listCurriculumDrafts(token),
      listSkillBundles(token),
    ]);
    setCandidates(c);
    setSynthesis(s);
    setPatches(p);
    setCurriculum(d);
    setSkills(k);
  }

  useEffect(() => { if (auth?.access_token) reload(auth.access_token); }, [auth]);

  async function seedCandidate() {
    await createCandidate(auth.access_token, {
      source_type: "learner_export",
      learner_id: "wesley-learner",
      pack_id: "biology-pack",
      candidate_kind: "hidden_prerequisite",
      title: "Probability intuition before drift",
      summary: "Learner evidence suggests drift is easier after explicit random-process intuition.",
      structured_payload: {
        affected_concept: "drift",
        prerequisites: ["variation", "random_walk"],
        source_concepts: ["drift", "variation"],
        expected_inputs: ["short explanation", "worked example"],
        failure_modes: ["treating drift as directional"],
        validation_checks: ["explains stochastic change"],
        canonical_examples: ["coin flip population drift example"]
      },
      evidence_summary: "Repeated learner confusion with stochastic interpretation.",
      confidence_hint: 0.78,
      novelty_score: 0.69,
      synthesis_score: 0.55,
      triage_lane: "pack_improvement"
    });
    await reload();
    setMessage("Seed candidate created.");
  }

  async function doPromote(candidateId, target) {
    await promoteCandidate(auth.access_token, candidateId, { promotion_target: target, target_object_id: "", promotion_status: "approved" });
    await reload();
    setMessage(`Candidate ${candidateId} promoted to ${target}.`);
  }

  async function doSynthesis() {
    await runSynthesis(auth.access_token, { source_pack_id: "biology-pack", target_pack_id: "math-pack", limit: 10 });
    await reload();
    setMessage("Synthesis run completed.");
  }

  async function doPromoteSynthesis(synthesisId) {
    await promoteSynthesis(auth.access_token, synthesisId, { promotion_target: "pack_improvement" });
    await reload();
    setMessage(`Synthesis ${synthesisId} promoted.`);
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Promotion target objects</h1>
          <p>Materialize promotions into patch proposals, curriculum drafts, and reusable skill bundles.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="toolbar">
          <button onClick={seedCandidate}>Seed candidate</button>
          <button onClick={doSynthesis}>Run synthesis</button>
          <button onClick={() => reload()}>Refresh</button>
        </div>
      </header>

      <main className="grid3">
        <section>
          <h2>Candidates</h2>
          <div className="stack">
            {candidates.map(c => <CandidateCard key={c.candidate_id} candidate={c} onPromote={doPromote} />)}
          </div>
        </section>
        <section>
          <h2>Synthesis</h2>
          <div className="stack">
            {synthesis.map(s => (
              <div className="card small" key={s.synthesis_id}>
                <h3>{s.source_concept_id} ↔ {s.target_concept_id}</h3>
                <div className="muted">{s.source_pack_id} → {s.target_pack_id}</div>
                <p>{s.explanation}</p>
                <button onClick={() => doPromoteSynthesis(s.synthesis_id)}>Promote synthesis</button>
              </div>
            ))}
          </div>
        </section>
        <section>
          <h2>Materialized outputs</h2>
          <div className="stack">
            <div className="card small"><h3>Pack patches</h3><pre>{JSON.stringify(patches, null, 2)}</pre></div>
            <div className="card small"><h3>Curriculum drafts</h3><pre>{JSON.stringify(curriculum, null, 2)}</pre></div>
            <div className="card small"><h3>Skill bundles</h3><pre>{JSON.stringify(skills, null, 2)}</pre></div>
          </div>
        </section>
      </main>
    </div>
  );
}
