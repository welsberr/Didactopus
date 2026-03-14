const API = "http://127.0.0.1:8011/api";

function authHeaders(token, json=true) {
  const h = { Authorization: `Bearer ${token}` };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export async function login(username, password) {
  const res = await fetch(`${API}/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
  if (!res.ok) throw new Error("login failed");
  return await res.json();
}
export async function refresh(refreshToken) {
  const res = await fetch(`${API}/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: refreshToken }) });
  if (!res.ok) throw new Error("refresh failed");
  return await res.json();
}
export async function fetchPacks(token) { const res = await fetch(`${API}/packs`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPacks failed"); return await res.json(); }
export async function fetchLearnerState(token, learnerId) { const res = await fetch(`${API}/learners/${learnerId}/state`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchLearnerState failed"); return await res.json(); }
export async function putLearnerState(token, learnerId, state) { const res = await fetch(`${API}/learners/${learnerId}/state`, { method: "PUT", headers: authHeaders(token), body: JSON.stringify(state) }); if (!res.ok) throw new Error("putLearnerState failed"); return await res.json(); }
export async function createLearnerRun(token, payload) { const res = await fetch(`${API}/learner-runs`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("createLearnerRun failed"); return await res.json(); }
export async function addWorkflowEvent(token, payload) { const res = await fetch(`${API}/workflow-events`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("addWorkflowEvent failed"); return await res.json(); }
export async function fetchAnimation(token, learnerId, packId) { const res = await fetch(`${API}/learners/${learnerId}/animation/${packId}`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchAnimation failed"); return await res.json(); }
