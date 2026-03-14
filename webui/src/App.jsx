import React, { useEffect, useState } from "react";
import { login, createCandidate, promoteCandidate, listPackPatches, listCurriculumDrafts, listSkillBundles, editPatch, applyPatch, editCurriculum, editSkill, listVersions, exportCurriculum, exportSkill } from "./api";

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
      <h1>Didactopus object versioning</h1>
      <label>Username<input value={username} onChange={(e)=>setUsername(e.target.value)} /></label>
      <label>Password<input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} /></label>
      <button className="primary" onClick={doLogin}>Login</button>
      {error ? <div className="error">{error}</div> : null}
    </section></div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(null);
  const [patches, setPatches] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [skills, setSkills] = useState([]);
  const [versions, setVersions] = useState([]);
  const [exports, setExports] = useState({});
  const [message, setMessage] = useState("");

  async function reload(token = auth?.access_token) {
    if (!token) return;
    const [p, d, s] = await Promise.all([listPackPatches(token), listCurriculumDrafts(token), listSkillBundles(token)]);
    setPatches(p); setDrafts(d); setSkills(s);
  }

  useEffect(() => { if (auth?.access_token) reload(auth.access_token); }, [auth]);

  async function seedAll() {
    const candidate = await createCandidate(auth.access_token, {
      source_type: "learner_export",
      learner_id: "wesley-learner",
      pack_id: "biology-pack",
      candidate_kind: "hidden_prerequisite",
      title: "Probability intuition before drift",
      summary: "Learner evidence suggests drift is easier after random-process intuition.",
      structured_payload: {
        affected_concept: "drift",
        suggested_prereq: "random_walk",
        source_concepts: ["drift", "variation"],
        prerequisites: ["variation", "random_walk"],
        expected_inputs: ["text", "example"],
        failure_modes: ["treating drift as directional"],
        validation_checks: ["explains stochastic change"],
        canonical_examples: ["coin-flip drift example"]
      },
      evidence_summary: "Repeated learner confusion with stochastic interpretation.",
      confidence_hint: 0.8,
      novelty_score: 0.7,
      synthesis_score: 0.6,
      triage_lane: "pack_improvement"
    });
    const candidateId = candidate.candidate_id;
    await promoteCandidate(auth.access_token, candidateId, { promotion_target: "pack_improvement", target_object_id: "", promotion_status: "approved" });

    const c2 = await createCandidate(auth.access_token, {
      source_type: "learner_export",
      learner_id: "wesley-learner",
      pack_id: "biology-pack",
      candidate_kind: "lesson_outline",
      title: "Intro lesson on stochastic evolutionary change",
      summary: "A lesson framing drift through random processes.",
      structured_payload: { source_concepts: ["drift", "variation", "random_walk"] },
      evidence_summary: "Good bridge opportunity for cross-pack synthesis.",
      confidence_hint: 0.72,
      novelty_score: 0.6,
      synthesis_score: 0.75,
      triage_lane: "curriculum_draft"
    });
    await promoteCandidate(auth.access_token, c2.candidate_id, { promotion_target: "curriculum_draft", target_object_id: "", promotion_status: "approved" });

    const c3 = await createCandidate(auth.access_token, {
      source_type: "learner_export",
      learner_id: "wesley-learner",
      pack_id: "biology-pack",
      candidate_kind: "skill_bundle_candidate",
      title: "Explain stochastic biological change",
      summary: "Skill for recognizing and explaining stochastic population change.",
      structured_payload: {
        prerequisites: ["variation", "random_walk"],
        expected_inputs: ["question", "scenario"],
        failure_modes: ["teleological explanation"],
        validation_checks: ["distinguishes drift from selection"],
        canonical_examples: ["small population allele frequency drift"]
      },
      evidence_summary: "Could be reusable as an agent skill.",
      confidence_hint: 0.74,
      novelty_score: 0.58,
      synthesis_score: 0.71,
      triage_lane: "reusable_skill_bundle"
    });
    await promoteCandidate(auth.access_token, c3.candidate_id, { promotion_target: "reusable_skill_bundle", target_object_id: "", promotion_status: "approved" });

    await reload();
    setMessage("Seeded patch, curriculum draft, and skill bundle.");
  }

  async function inspectVersions(kind, id) {
    const data = await listVersions(auth.access_token, kind, id);
    setVersions(data);
  }

  async function revisePatch(id) {
    await editPatch(auth.access_token, id, {
      payload: { reviewer_notes: "Elevated priority after synthesis review.", status: "approved" },
      note: "Reviewer note update"
    });
    await reload();
  }

  async function applySelectedPatch(id) {
    await applyPatch(auth.access_token, id, { note: "Merged into pack JSON" });
    await reload();
  }

  async function reviseDraft(id) {
    await editCurriculum(auth.access_token, id, {
      payload: { editorial_notes: "Add random-walk bridge example.", status: "editorial_review" },
      note: "Editorial refinement"
    });
    await reload();
  }

  async function reviseSkill(id) {
    await editSkill(auth.access_token, id, {
      payload: { status: "validation", validation_checks: ["distinguishes drift from selection", "uses stochastic terminology correctly"] },
      note: "Validation criteria strengthened"
    });
    await reload();
  }

  async function doExportDraft(id) {
    const out = await exportCurriculum(auth.access_token, id);
    setExports(prev => ({ ...prev, ["draft:"+id]: out }));
  }

  async function doExportSkill(id) {
    const out = await exportSkill(auth.access_token, id);
    setExports(prev => ({ ...prev, ["skill:"+id]: out }));
  }

  if (!auth) return <LoginView onAuth={setAuth} />;

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Object editing, versioning, apply, and export</h1>
          <p>Promoted objects can now be revised, versioned, merged into packs, and exported in reusable formats.</p>
          <div className="muted">{message}</div>
        </div>
        <div className="toolbar">
          <button onClick={seedAll}>Seed all objects</button>
          <button onClick={() => reload()}>Refresh</button>
        </div>
      </header>

      <main className="grid3">
        <section>
          <h2>Pack patches</h2>
          <div className="stack">
            {patches.map(p => (
              <div key={p.patch_id} className="card small">
                <h3>{p.title}</h3>
                <div className="muted">v{p.current_version} · {p.status}</div>
                <pre>{JSON.stringify(p.proposed_change, null, 2)}</pre>
                <button onClick={() => revisePatch(p.patch_id)}>Revise</button>
                <button onClick={() => applySelectedPatch(p.patch_id)}>Apply to pack</button>
                <button onClick={() => inspectVersions("pack_patch", p.patch_id)}>Versions</button>
              </div>
            ))}
          </div>
        </section>
        <section>
          <h2>Curriculum drafts</h2>
          <div className="stack">
            {drafts.map(d => (
              <div key={d.draft_id} className="card small">
                <h3>{d.topic_focus}</h3>
                <div className="muted">v{d.current_version} · {d.status}</div>
                <pre>{d.content_markdown}</pre>
                <button onClick={() => reviseDraft(d.draft_id)}>Revise</button>
                <button onClick={() => inspectVersions("curriculum_draft", d.draft_id)}>Versions</button>
                <button onClick={() => doExportDraft(d.draft_id)}>Export</button>
                {exports["draft:"+d.draft_id] ? <pre>{JSON.stringify(exports["draft:"+d.draft_id], null, 2)}</pre> : null}
              </div>
            ))}
            <h2>Skill bundles</h2>
            {skills.map(s => (
              <div key={s.skill_bundle_id} className="card small">
                <h3>{s.skill_name}</h3>
                <div className="muted">v{s.current_version} · {s.status}</div>
                <pre>{JSON.stringify(s, null, 2)}</pre>
                <button onClick={() => reviseSkill(s.skill_bundle_id)}>Revise</button>
                <button onClick={() => inspectVersions("skill_bundle", s.skill_bundle_id)}>Versions</button>
                <button onClick={() => doExportSkill(s.skill_bundle_id)}>Export</button>
                {exports["skill:"+s.skill_bundle_id] ? <pre>{JSON.stringify(exports["skill:"+s.skill_bundle_id], null, 2)}</pre> : null}
              </div>
            ))}
          </div>
        </section>
        <section>
          <h2>Version history</h2>
          <div className="card small">
            <pre>{JSON.stringify(versions, null, 2)}</pre>
          </div>
        </section>
      </main>
    </div>
  );
}
