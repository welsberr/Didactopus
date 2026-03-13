import React, { useMemo, useState } from "react";
import reviewData from "../sample/review_data.json";

const statuses = ["needs_review", "trusted", "provisional", "rejected"];

function downloadJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function promotedPackFromState(state) {
  return {
    pack: {
      ...state.pack,
      version: String(state.pack.version || "0.1.0-draft").replace("-draft", "-reviewed"),
      curation: {
        reviewer: state.reviewer,
        ledger_entries: state.ledger.length
      }
    },
    concepts: state.concepts
      .filter((c) => c.status !== "rejected")
      .map((c) => ({
        id: c.concept_id,
        title: c.title,
        description: c.description,
        prerequisites: c.prerequisites,
        mastery_signals: c.mastery_signals,
        status: c.status,
        notes: c.notes,
        mastery_profile: {}
      })),
    conflicts: state.conflicts,
    review_flags: state.review_flags
  };
}

export default function App() {
  const [state, setState] = useState(reviewData);
  const [selectedId, setSelectedId] = useState(reviewData.concepts[0]?.concept_id || "");
  const selected = useMemo(
    () => state.concepts.find((c) => c.concept_id === selectedId) || null,
    [state, selectedId]
  );

  function updateConcept(conceptId, patch, rationale) {
    setState((prev) => {
      const concepts = prev.concepts.map((c) =>
        c.concept_id === conceptId ? { ...c, ...patch } : c
      );
      const ledger = [
        ...prev.ledger,
        {
          reviewer: prev.reviewer,
          action: {
            action_type: "note",
            target: conceptId,
            payload: patch,
            rationale: rationale || "UI edit"
          }
        }
      ];
      return { ...prev, concepts, ledger };
    });
  }

  function resolveConflict(conflict) {
    setState((prev) => ({
      ...prev,
      conflicts: prev.conflicts.filter((c) => c !== conflict),
      ledger: [
        ...prev.ledger,
        {
          reviewer: prev.reviewer,
          action: {
            action_type: "resolve_conflict",
            target: "",
            payload: { conflict },
            rationale: "Resolved in UI"
          }
        }
      ]
    }));
  }

  const promoted = promotedPackFromState(state);

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus Review UI</h1>
          <p>
            Reduce the activation-energy hump: move from raw course-derived draft pack
            to curated reviewed domain pack with less friction.
          </p>
        </div>
        <div className="hero-actions">
          <button onClick={() => downloadJson("review_data.edited.json", state)}>Export Review State</button>
          <button onClick={() => downloadJson("promoted_pack.json", promoted)}>Export Promoted Pack</button>
        </div>
      </header>

      <section className="summary-grid">
        <div className="card">
          <h2>Pack</h2>
          <div className="small">{state.pack.display_name || state.pack.name}</div>
          <div className="small">Reviewer: {state.reviewer}</div>
          <div className="small">Concepts: {state.concepts.length}</div>
        </div>
        <div className="card">
          <h2>Conflicts</h2>
          <div className="big">{state.conflicts.length}</div>
        </div>
        <div className="card">
          <h2>Flags</h2>
          <div className="big">{state.review_flags.length}</div>
        </div>
        <div className="card">
          <h2>Ledger</h2>
          <div className="big">{state.ledger.length}</div>
        </div>
      </section>

      <main className="layout">
        <aside className="sidebar">
          <h2>Concepts</h2>
          {state.concepts.map((c) => (
            <button
              key={c.concept_id}
              className={`concept-btn ${c.concept_id === selectedId ? "active" : ""}`}
              onClick={() => setSelectedId(c.concept_id)}
            >
              <span>{c.title}</span>
              <span className={`status-pill status-${c.status}`}>{c.status}</span>
            </button>
          ))}
        </aside>

        <section className="content">
          {selected ? (
            <>
              <div className="card">
                <h2>Concept Editor</h2>
                <label>
                  Title
                  <input
                    value={selected.title}
                    onChange={(e) => updateConcept(selected.concept_id, { title: e.target.value }, "Edited title")}
                  />
                </label>
                <label>
                  Status
                  <select
                    value={selected.status}
                    onChange={(e) => updateConcept(selected.concept_id, { status: e.target.value }, "Changed trust status")}
                  >
                    {statuses.map((s) => (
                      <option value={s} key={s}>{s}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Description
                  <textarea
                    rows="6"
                    value={selected.description}
                    onChange={(e) => updateConcept(selected.concept_id, { description: e.target.value }, "Edited description")}
                  />
                </label>
                <label>
                  Prerequisites (comma-separated ids)
                  <input
                    value={(selected.prerequisites || []).join(", ")}
                    onChange={(e) =>
                      updateConcept(
                        selected.concept_id,
                        {
                          prerequisites: e.target.value
                            .split(",")
                            .map((x) => x.trim())
                            .filter(Boolean)
                        },
                        "Edited prerequisites"
                      )
                    }
                  />
                </label>
                <label>
                  Notes
                  <textarea
                    rows="4"
                    value={(selected.notes || []).join("\n")}
                    onChange={(e) =>
                      updateConcept(
                        selected.concept_id,
                        { notes: e.target.value.split("\n").filter(Boolean) },
                        "Edited notes"
                      )
                    }
                  />
                </label>
              </div>

              <div className="card">
                <h2>Mastery Signals</h2>
                <ul>
                  {(selected.mastery_signals || []).map((signal, idx) => (
                    <li key={idx}>{signal}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <div className="card">No concept selected.</div>
          )}
        </section>

        <section className="rightbar">
          <div className="card">
            <h2>Conflicts</h2>
            {state.conflicts.length ? state.conflicts.map((conflict, idx) => (
              <div key={idx} className="conflict">
                <div>{conflict}</div>
                <button onClick={() => resolveConflict(conflict)}>Resolve</button>
              </div>
            )) : <div className="small">No remaining conflicts.</div>}
          </div>

          <div className="card">
            <h2>Review Flags</h2>
            <ul>
              {state.review_flags.map((flag, idx) => <li key={idx}>{flag}</li>)}
            </ul>
          </div>

          <div className="card">
            <h2>Why this exists</h2>
            <p className="small">
              Online course material can be excellent and still be hard to activate.
              Didactopus aims to reduce the setup burden from “useful but messy course content”
              to “usable reviewed learning domain.”
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
