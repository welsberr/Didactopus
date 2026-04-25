import React, { useEffect, useMemo, useState } from "react";
import {
  login,
  listCandidates,
  createCandidate,
  createReview,
  promoteCandidate,
  runSynthesis,
  listSynthesisCandidates,
  promoteSynthesis,
  createLearnerWorkbenchSession,
} from "./api";
import {
  applyEvidence,
  buildMasteryMap,
  progressPercent,
  recommendNext,
  milestoneMessages,
  claimReadiness,
} from "./engine";

function LauncherView({ onSelect }) {
  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Didactopus</p>
          <h1>Choose a work mode.</h1>
          <p>
            The current prototype now has two distinct entry points: the existing review workbench
            and a learner-workbench pilot using the evo-edu `Evidence Trail` pack.
          </p>
        </div>
        <div className="toolbar">
          <button className="primary" onClick={() => onSelect("learner")}>Open learner pilot</button>
          <button onClick={() => onSelect("review")}>Open review workbench</button>
        </div>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Learner workbench pilot</h2>
          <p>
            Use a guided-study surface built around question framing, source comparison, and
            revision under uncertainty.
          </p>
          <ul className="plain-list">
            <li>Loads the `Evidence Trail` pack.</li>
            <li>Shows concept path and onboarding.</li>
            <li>Separates observation from interpretation.</li>
            <li>Treats revision as normal progress.</li>
          </ul>
        </section>
        <section className="card">
          <h2>Review workbench</h2>
          <p>
            Keep using the existing knowledge-candidate and synthesis workflow for pack-improvement
            and review operations.
          </p>
          <ul className="plain-list">
            <li>Review learner-derived candidates.</li>
            <li>Promote pack improvements and skill bundles.</li>
            <li>Inspect synthesis candidates across packs.</li>
          </ul>
        </section>
      </main>
    </div>
  );
}

function LoginView({ onAuth, onBack }) {
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
        <p className="eyebrow">Review Workbench</p>
        <h1>Didactopus review workbench</h1>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <div className="toolbar">
          <button className="primary" onClick={doLogin}>Login</button>
          <button onClick={onBack}>Back</button>
        </div>
        {error ? <div className="error">{error}</div> : null}
      </section>
    </div>
  );
}

function CandidateCard({ candidate, onReview, onPromote }) {
  return (
    <div className="card small">
      <h3>{candidate.title}</h3>
      <div className="muted">
        {candidate.candidate_kind} · lane: {candidate.triage_lane} · status: {candidate.current_status}
      </div>
      <p>{candidate.summary}</p>
      <div className="tiny">
        confidence {candidate.confidence_hint.toFixed(2)} · novelty {candidate.novelty_score.toFixed(2)} · synthesis {candidate.synthesis_score.toFixed(2)}
      </div>
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
      <div className="tiny">
        total {item.score_total.toFixed(2)} · semantic {item.score_semantic.toFixed(2)} · structural {item.score_structural.toFixed(2)}
      </div>
      <button onClick={() => onPromote(item.synthesis_id)}>Promote into workflow</button>
    </div>
  );
}

function ReviewWorkbench({ auth, onBack }) {
  const [candidates, setCandidates] = useState([]);
  const [synthesis, setSynthesis] = useState([]);
  const [message, setMessage] = useState("");

  async function reload(token = auth?.access_token) {
    if (!token) return;
    setCandidates(await listCandidates(token));
    setSynthesis(await listSynthesisCandidates(token));
  }

  useEffect(() => {
    if (auth?.access_token) reload(auth.access_token);
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
      triage_lane: "pack_improvement",
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
      requested_changes: "",
    });
    await reload();
    setMessage(`Review added to candidate ${candidateId}.`);
  }

  async function handlePromote(candidateId, target) {
    await promoteCandidate(auth.access_token, candidateId, {
      promotion_target: target,
      target_object_id: "",
      promotion_status: "approved",
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

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Review Workbench</p>
          <h1>Review workbench + synthesis engine</h1>
          <p>
            Triages learner-derived knowledge into pack improvements, curriculum drafts, skill bundles,
            or archive, while surfacing cross-pack synthesis proposals.
          </p>
          <div className="muted">{message}</div>
        </div>
        <div className="toolbar">
          <button className="primary" onClick={seedCandidate}>Seed candidate</button>
          <button onClick={handleRunSynthesis}>Run synthesis</button>
          <button onClick={() => reload()}>Refresh</button>
          <button onClick={onBack}>Back</button>
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

function LearnerWorkbench({ onBack }) {
  const [pack, setPack] = useState(null);
  const [error, setError] = useState("");
  const [currentConceptId, setCurrentConceptId] = useState("");
  const [learnerState, setLearnerState] = useState({ records: [], history: [] });
  const [question, setQuestion] = useState("");
  const [observation, setObservation] = useState("");
  const [interpretation, setInterpretation] = useState("");
  const [uncertainty, setUncertainty] = useState("");
  const [revisionTrigger, setRevisionTrigger] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [sessionOutput, setSessionOutput] = useState(null);

  useEffect(() => {
    let active = true;
    fetch("/packs/evidence-trail-pack.json")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load evidence-trail pack");
        return res.json();
      })
      .then((data) => {
        if (!active) return;
        setPack(data);
        setCurrentConceptId(data.concepts?.[0]?.id || "");
      })
      .catch(() => {
        if (!active) return;
        setError("Could not load the learner-workbench pack.");
      });
    return () => {
      active = false;
    };
  }, []);

  const currentConcept = useMemo(
    () => pack?.concepts?.find((concept) => concept.id === currentConceptId) || null,
    [pack, currentConceptId]
  );

  const nextConcept = useMemo(() => {
    if (!pack?.concepts || !currentConcept) return null;
    const index = pack.concepts.findIndex((concept) => concept.id === currentConcept.id);
    return index >= 0 ? pack.concepts[index + 1] || null : null;
  }, [pack, currentConcept]);

  const masteryMap = useMemo(
    () => (pack ? buildMasteryMap(learnerState, pack) : []),
    [learnerState, pack]
  );
  const progress = useMemo(
    () => (pack ? progressPercent(learnerState, pack) : 0),
    [learnerState, pack]
  );
  const nextCards = useMemo(
    () => (pack ? recommendNext(learnerState, pack) : []),
    [learnerState, pack]
  );
  const readiness = useMemo(
    () => (pack ? claimReadiness(learnerState, pack) : null),
    [learnerState, pack]
  );
  const milestones = useMemo(
    () => (pack ? milestoneMessages(learnerState, pack) : []),
    [learnerState, pack]
  );

  function advanceConcept() {
    if (nextConcept) setCurrentConceptId(nextConcept.id);
  }

  async function evaluateCurrentWork() {
    const score =
      (question.trim() ? 0.18 : 0) +
      (observation.trim() ? 0.24 : 0) +
      (interpretation.trim() ? 0.20 : 0) +
      (uncertainty.trim() ? 0.18 : 0) +
      (revisionTrigger.trim() ? 0.20 : 0);
    const confidenceHint =
      0.45 +
      (observation.trim() ? 0.10 : 0) +
      (interpretation.trim() ? 0.08 : 0) +
      (uncertainty.trim() ? 0.08 : 0) +
      (revisionTrigger.trim() ? 0.09 : 0);

    const nextState = applyEvidence(learnerState, {
      concept_id: currentConcept.id,
      dimension: currentConcept.masteryDimension || "mastery",
      score: Math.min(1, score),
      confidence_hint: Math.min(1, confidenceHint),
      timestamp: new Date().toISOString(),
      note: "Evidence Trail learner-workbench submission",
    });
    setLearnerState(nextState);

    try {
      const session = await createLearnerWorkbenchSession({
        pack_id: pack.id,
        concept_id: currentConcept.id,
        learner_goal: question || `Work through ${currentConcept.title} in the Evidence Trail pack.`,
        question,
        observation,
        interpretation,
        uncertainty,
        revision_trigger: revisionTrigger,
      });
      setFeedback({
        strengths: session.feedback?.strengths || [],
        gaps: session.feedback?.gaps || [],
        nextRevision: session.feedback?.next_revision_target || "Compare one more source or example before moving on.",
      });
      setSessionOutput(session);
    } catch {
      setFeedback({
        strengths: [],
        gaps: ["Backend session generation failed; local progress was still recorded."],
        nextRevision: "Check the learner-workbench API path and retry.",
      });
      setSessionOutput(null);
    }
  }

  if (error) {
    return (
      <div className="page narrow">
        <section className="card">
          <h1>Learner workbench pilot</h1>
          <div className="error">{error}</div>
          <button onClick={onBack}>Back</button>
        </section>
      </div>
    );
  }

  if (!pack || !currentConcept) {
    return (
      <div className="page narrow">
        <section className="card">
          <h1>Learner workbench pilot</h1>
          <p>Loading the `Evidence Trail` pack...</p>
        </section>
      </div>
    );
  }

  return (
    <div className="page learner-page">
      <header className="hero learner-hero">
        <div>
          <p className="eyebrow">Learner Workbench Pilot</p>
          <h1>{pack.title}</h1>
          <p>{pack.subtitle}</p>
          <div className="muted">
            This pilot uses scientific virtues as operating rules: separate observation from interpretation,
            preserve uncertainty, and treat revision as progress.
          </div>
        </div>
        <div className="toolbar">
          <button className="primary" onClick={advanceConcept} disabled={!nextConcept}>
            {nextConcept ? `Next: ${nextConcept.title}` : "At final concept"}
          </button>
          <button onClick={onBack}>Back</button>
        </div>
      </header>

      <main className="learner-grid">
        <section className="card">
          <p className="eyebrow">Onboarding</p>
          <h2>{pack.onboarding.headline}</h2>
          <p>{pack.onboarding.body}</p>
          <div className="progress-strip">
            <strong>Progress:</strong> {progress}% · {readiness?.mastered ?? 0}/{pack.concepts.length} concepts strongly supported
          </div>
          <ul className="plain-list">
            {pack.onboarding.checklist.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="card">
          <p className="eyebrow">Concept Path</p>
          <div className="concept-path">
            {pack.concepts.map((concept, index) => (
              <button
                key={concept.id}
                className={`concept-chip${concept.id === currentConceptId ? " active" : ""}`}
                onClick={() => setCurrentConceptId(concept.id)}
              >
                {concept.title}
                <span className="chip-status">
                  {masteryMap[index]?.status || "locked"}
                </span>
              </button>
            ))}
          </div>
          <div className="concept-focus">
            <h3>{currentConcept.title}</h3>
            <div className="tiny">
              Prerequisites: {currentConcept.prerequisites.length ? currentConcept.prerequisites.join(", ") : "none explicit"}
            </div>
            <p className="muted">{currentConcept.exerciseReward}</p>
          </div>
        </section>

        <section className="card learner-form">
          <p className="eyebrow">Current Study Record</p>
          <h2>Keep observation and interpretation distinct.</h2>
          <label>
            Question
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What are you trying to understand or test?" />
          </label>
          <label>
            Observation
            <textarea value={observation} onChange={(e) => setObservation(e.target.value)} placeholder="What did the model, species record, or source actually show?" />
          </label>
          <label>
            Interpretation
            <textarea value={interpretation} onChange={(e) => setInterpretation(e.target.value)} placeholder="What explanation currently fits best?" />
          </label>
          <label>
            Uncertainty
            <textarea value={uncertainty} onChange={(e) => setUncertainty(e.target.value)} placeholder="What remains unclear, weakly supported, or unresolved?" />
          </label>
          <label>
            Revision trigger
            <textarea value={revisionTrigger} onChange={(e) => setRevisionTrigger(e.target.value)} placeholder="What evidence or comparison would make you revise your current view?" />
          </label>
          <div className="toolbar">
            <button className="primary" onClick={evaluateCurrentWork}>Evaluate this step</button>
          </div>
        </section>

        <section className="card">
          <p className="eyebrow">Virtues In Use</p>
          <div className="virtue-grid">
            <div className="virtue-card">
              <strong>Curiosity</strong>
              <p>Keep the question open long enough to learn from the evidence.</p>
            </div>
            <div className="virtue-card">
              <strong>Honesty</strong>
              <p>Write down what you actually observed before polishing an explanation.</p>
            </div>
            <div className="virtue-card">
              <strong>Skepticism</strong>
              <p>Ask whether the current claim is well supported or only convenient.</p>
            </div>
            <div className="virtue-card">
              <strong>Revision</strong>
              <p>Treat changed conclusions as progress, not as failure.</p>
            </div>
          </div>
        </section>

        <section className="card">
          <p className="eyebrow">Evaluator Feedback</p>
          <h2>Trust-preserving critique</h2>
          {feedback ? (
            <>
              <div className="feedback-block">
                <strong>Strengths</strong>
                <ul className="plain-list">
                  {feedback.strengths.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
              <div className="feedback-block">
                <strong>Revision targets</strong>
                <ul className="plain-list">
                  {feedback.gaps.length ? feedback.gaps.map((item) => <li key={item}>{item}</li>) : <li>No immediate gap detected; extend with another source comparison.</li>}
                </ul>
              </div>
              <div className="compliance-note">
                <strong>Next revision target:</strong> {feedback.nextRevision}
              </div>
            </>
          ) : (
            <p className="muted">Submit a study record to get evaluator-style feedback grounded in the current concept and scientific-virtues framing.</p>
          )}
        </section>

        <section className="card">
          <p className="eyebrow">Backend Session Output</p>
          <h2>Grounded mentor/practice/evaluator loop</h2>
          {sessionOutput ? (
            <div className="resource-list">
              <div className="next-card">
                <strong>Mentor</strong>
                <p>{sessionOutput.mentor?.text}</p>
              </div>
              <div className="next-card">
                <strong>Practice</strong>
                <p>{sessionOutput.practice?.text}</p>
              </div>
              <div className="next-card">
                <strong>Evaluator</strong>
                <p>{sessionOutput.evaluator?.text}</p>
              </div>
              <div className="next-card">
                <strong>Next step</strong>
                <p>{sessionOutput.next_step?.text}</p>
              </div>
            </div>
          ) : (
            <p className="muted">Run an evaluation to request grounded mentor, practice, evaluator, and next-step text from the backend session endpoint.</p>
          )}
        </section>

        <section className="card">
          <p className="eyebrow">Next Study Action</p>
          <h2>{nextConcept ? nextConcept.title : "Complete the current concept carefully"}</h2>
          <p>
            {nextConcept
              ? `Move forward when you can justify your interpretation and name what evidence would change it. The next concept extends this work into ${nextConcept.title.toLowerCase()}.`
              : "You are at the end of the current concept path. Review your uncertainty and revision trigger before treating the topic as settled."}
          </p>
          <div className="resource-list">
            {nextCards.map((card) => (
              <div className="next-card" key={card.id}>
                <strong>{card.title}</strong>
                <p>{card.reason}</p>
                <div className="tiny">{card.why.join(" · ")}</div>
              </div>
            ))}
          </div>
          <div className="feedback-block">
            <strong>Milestones</strong>
            <ul className="plain-list">
              {milestones.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </div>
          <div className="compliance-note">
            <strong>Source posture:</strong> {pack.compliance.sources} linked sources; attribution required: {pack.compliance.attributionRequired ? "yes" : "no"}.
          </div>
        </section>
      </main>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState("launcher");
  const [auth, setAuth] = useState(null);

  if (mode === "learner") return <LearnerWorkbench onBack={() => setMode("launcher")} />;
  if (mode === "review" && !auth) {
    return <LoginView onAuth={setAuth} onBack={() => setMode("launcher")} />;
  }
  if (mode === "review" && auth) {
    return <ReviewWorkbench auth={auth} onBack={() => { setAuth(null); setMode("launcher"); }} />;
  }
  return <LauncherView onSelect={setMode} />;
}
