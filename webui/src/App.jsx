import React, { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8765";
const statuses = ["needs_review", "trusted", "provisional", "rejected"];

export default function App() {
  const [registry, setRegistry] = useState({ workspaces: [], recent_workspace_ids: [] });
  const [workspaceId, setWorkspaceId] = useState("");
  const [workspaceTitle, setWorkspaceTitle] = useState("");
  const [importSource, setImportSource] = useState("");
  const [importPreview, setImportPreview] = useState(null);
  const [allowOverwrite, setAllowOverwrite] = useState(false);
  const [session, setSession] = useState(null);
  const [selectedId, setSelectedId] = useState("");
  const [pendingActions, setPendingActions] = useState([]);
  const [message, setMessage] = useState("Connecting to local Didactopus bridge...");

  async function loadRegistry() {
    const res = await fetch(`${API}/api/workspaces`);
    const data = await res.json();
    setRegistry(data);
    if (!session) setMessage("Choose, create, preview, or import a workspace.");
  }

  useEffect(() => {
    loadRegistry().catch(() => setMessage("Could not connect to local review bridge. Start the Python bridge service first."));
  }, []);

  async function createWorkspace() {
    if (!workspaceId || !workspaceTitle) return;
    await fetch(`${API}/api/workspaces/create`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ workspace_id: workspaceId, title: workspaceTitle })
    });
    await loadRegistry();
    await openWorkspace(workspaceId);
  }

  async function previewImport() {
    if (!workspaceId || !importSource) return;
    const res = await fetch(`${API}/api/workspaces/import-preview`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ workspace_id: workspaceId, source_dir: importSource })
    });
    const data = await res.json();
    setImportPreview(data);
    setMessage(data.ok ? "Import preview ready." : "Import preview found blocking errors.");
  }

  async function importWorkspace() {
    if (!workspaceId || !importSource) return;
    const res = await fetch(`${API}/api/workspaces/import`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        workspace_id: workspaceId,
        title: workspaceTitle || workspaceId,
        source_dir: importSource,
        allow_overwrite: allowOverwrite
      })
    });
    const data = await res.json();
    if (!data.ok) {
      setMessage(data.error || "Import failed.");
      return;
    }
    await loadRegistry();
    await openWorkspace(workspaceId);
    setMessage(`Imported draft pack from ${importSource} into workspace ${workspaceId}.`);
  }

  async function openWorkspace(id) {
    const res = await fetch(`${API}/api/workspaces/open`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ workspace_id: id })
    });
    const opened = await res.json();
    if (!opened.ok) {
      setMessage("Could not open workspace.");
      return;
    }
    const sessionRes = await fetch(`${API}/api/load`);
    const sessionData = await sessionRes.json();
    setSession(sessionData.session);
    setSelectedId(sessionData.session?.draft_pack?.concepts?.[0]?.concept_id || "");
    setPendingActions([]);
    setMessage(`Opened workspace ${id}.`);
    await loadRegistry();
  }

  const selected = useMemo(() => {
    if (!session) return null;
    return session.draft_pack.concepts.find((c) => c.concept_id === selectedId) || null;
  }, [session, selectedId]);

  function queueAction(action) {
    setPendingActions((prev) => [...prev, action]);
  }

  function patchConcept(conceptId, patch, rationale) {
    if (!session) return;
    const concepts = session.draft_pack.concepts.map((c) =>
      c.concept_id === conceptId ? { ...c, ...patch } : c
    );
    setSession({ ...session, draft_pack: { ...session.draft_pack, concepts } });

    if (patch.status !== undefined) queueAction({ action_type: "set_status", target: conceptId, payload: { status: patch.status }, rationale });
    if (patch.title !== undefined) queueAction({ action_type: "edit_title", target: conceptId, payload: { title: patch.title }, rationale });
    if (patch.description !== undefined) queueAction({ action_type: "edit_description", target: conceptId, payload: { description: patch.description }, rationale });
    if (patch.prerequisites !== undefined) queueAction({ action_type: "edit_prerequisites", target: conceptId, payload: { prerequisites: patch.prerequisites }, rationale });
    if (patch.notes !== undefined) queueAction({ action_type: "edit_notes", target: conceptId, payload: { notes: patch.notes }, rationale });
  }

  function resolveConflict(conflict) {
    if (!session) return;
    setSession({
      ...session,
      draft_pack: { ...session.draft_pack, conflicts: session.draft_pack.conflicts.filter((c) => c !== conflict) }
    });
    queueAction({ action_type: "resolve_conflict", target: "", payload: { conflict }, rationale: "Resolved in UI" });
  }

  async function saveChanges() {
    if (!pendingActions.length) {
      setMessage("No pending changes to save.");
      return;
    }
    const res = await fetch(`${API}/api/save`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ actions: pendingActions })
    });
    const data = await res.json();
    setSession(data.session);
    setPendingActions([]);
    setMessage("Saved review state.");
  }

  async function exportPromoted() {
    const res = await fetch(`${API}/api/export`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({})
    });
    const data = await res.json();
    setMessage(`Exported promoted pack to ${data.promoted_pack_dir}`);
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <h1>Didactopus Graph QA</h1>
          <p>
            Reduce the activation-energy hump from generated draft packs to curated review workspaces
            by surfacing prerequisite-graph problems before import.
          </p>
          <div className="small">{message}</div>
        </div>
        <div className="hero-actions">
          <button onClick={saveChanges}>Save Review State</button>
          <button onClick={exportPromoted} disabled={!session}>Export Promoted Pack</button>
        </div>
      </header>

      <section className="summary-grid">
        <div className="card">
          <h2>Create Workspace</h2>
          <label>Workspace ID<input value={workspaceId} onChange={(e) => setWorkspaceId(e.target.value)} /></label>
          <label>Title<input value={workspaceTitle} onChange={(e) => setWorkspaceTitle(e.target.value)} /></label>
          <button onClick={createWorkspace}>Create</button>
        </div>
        <div className="card">
          <h2>Preview / Import Draft Pack</h2>
          <label>Workspace ID<input value={workspaceId} onChange={(e) => setWorkspaceId(e.target.value)} /></label>
          <label>Draft Pack Source Directory<input value={importSource} onChange={(e) => setImportSource(e.target.value)} placeholder="e.g. generated-pack" /></label>
          <label className="checkline"><input type="checkbox" checked={allowOverwrite} onChange={(e) => setAllowOverwrite(e.target.checked)} /> Allow overwrite of existing workspace draft_pack</label>
          <div className="button-row">
            <button onClick={previewImport}>Preview</button>
            <button onClick={importWorkspace}>Import</button>
          </div>
        </div>
        <div className="card">
          <h2>Recent</h2>
          <ul>{registry.recent_workspace_ids.map((id) => <li key={id}><button onClick={() => openWorkspace(id)}>{id}</button></li>)}</ul>
        </div>
        <div className="card">
          <h2>All Workspaces</h2>
          <ul>{registry.workspaces.map((ws) => <li key={ws.workspace_id}><button onClick={() => openWorkspace(ws.workspace_id)}>{ws.title} ({ws.workspace_id})</button></li>)}</ul>
        </div>
      </section>

      {importPreview && (
        <section className="preview-grid">
          <div className="card">
            <h2>Import Preview</h2>
            <div><strong>OK:</strong> {String(importPreview.ok)}</div>
            <div><strong>Overwrite Required:</strong> {String(importPreview.overwrite_required)}</div>
            <div><strong>Pack:</strong> {importPreview.summary?.display_name || importPreview.summary?.pack_name || "-"}</div>
            <div><strong>Version:</strong> {importPreview.summary?.version || "-"}</div>
            <div><strong>Concepts:</strong> {importPreview.summary?.concept_count ?? "-"}</div>
          </div>
          <div className="card">
            <h2>Validation Errors</h2>
            <ul>{(importPreview.errors || []).length ? importPreview.errors.map((x, i) => <li key={i}>{x}</li>) : <li>none</li>}</ul>
          </div>
          <div className="card">
            <h2>Semantic QA Warnings</h2>
            <ul>{(importPreview.semantic_warnings || []).length ? importPreview.semantic_warnings.map((x, i) => <li key={i}>{x}</li>) : <li>none</li>}</ul>
          </div>
          <div className="card">
            <h2>Graph QA Warnings</h2>
            <ul>{(importPreview.graph_warnings || []).length ? importPreview.graph_warnings.map((x, i) => <li key={i}>{x}</li>) : <li>none</li>}</ul>
          </div>
        </section>
      )}

      {session && (
        <main className="layout">
          <aside className="sidebar">
            <h2>Concepts</h2>
            {session.draft_pack.concepts.map((c) => (
              <button key={c.concept_id} className={`concept-btn ${c.concept_id === selectedId ? "active" : ""}`} onClick={() => setSelectedId(c.concept_id)}>
                <span>{c.title}</span>
                <span className={`status-pill status-${c.status}`}>{c.status}</span>
              </button>
            ))}
          </aside>

          <section className="content">
            {selected && (
              <div className="card">
                <h2>Concept Editor</h2>
                <label>Title<input value={selected.title} onChange={(e) => patchConcept(selected.concept_id, { title: e.target.value }, "Edited title")} /></label>
                <label>Status
                  <select value={selected.status} onChange={(e) => patchConcept(selected.concept_id, { status: e.target.value }, "Changed trust status")}>
                    {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </label>
                <label>Description<textarea rows="6" value={selected.description} onChange={(e) => patchConcept(selected.concept_id, { description: e.target.value }, "Edited description")} /></label>
                <label>Prerequisites (comma-separated ids)<input value={(selected.prerequisites || []).join(", ")} onChange={(e) => patchConcept(selected.concept_id, { prerequisites: e.target.value.split(",").map((x) => x.trim()).filter(Boolean) }, "Edited prerequisites")} /></label>
                <label>Notes (one per line)<textarea rows="4" value={(selected.notes || []).join("\n")} onChange={(e) => patchConcept(selected.concept_id, { notes: e.target.value.split("\n").filter(Boolean) }, "Edited notes")} /></label>
              </div>
            )}
          </section>

          <section className="rightbar">
            <div className="card">
              <h2>Conflicts</h2>
              {session.draft_pack.conflicts.length ? session.draft_pack.conflicts.map((conflict, idx) => (
                <div key={idx} className="conflict">
                  <div>{conflict}</div>
                  <button onClick={() => resolveConflict(conflict)}>Resolve</button>
                </div>
              )) : <div className="small">No remaining conflicts.</div>}
            </div>
            <div className="card">
              <h2>Review Flags</h2>
              <ul>{session.draft_pack.review_flags.map((flag, idx) => <li key={idx}>{flag}</li>)}</ul>
            </div>
          </section>
        </main>
      )}
    </div>
  );
}
