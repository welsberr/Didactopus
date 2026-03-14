const API = "http://127.0.0.1:8011/api";

function authHeaders(token, json=true) {
  const h = { "Authorization": `Bearer ${token}` };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export async function login(username, password) {
  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error("Login failed");
  return await res.json();
}

export async function refresh(refreshToken) {
  const res = await fetch(`${API}/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  if (!res.ok) throw new Error("Refresh failed");
  return await res.json();
}

export async function fetchPacks(token) {
  const res = await fetch(`${API}/packs`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("fetchPacks failed");
  return await res.json();
}

export async function fetchAdminPacks(token) {
  const res = await fetch(`${API}/admin/packs`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("fetchAdminPacks failed");
  return await res.json();
}

export async function upsertPack(token, payload) {
  const res = await fetch(`${API}/admin/packs`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("upsertPack failed");
  return await res.json();
}

export async function publishPack(token, packId, isPublished) {
  const res = await fetch(`${API}/admin/packs/${packId}/publish?is_published=${isPublished}`, {
    method: "POST",
    headers: authHeaders(token, false)
  });
  if (!res.ok) throw new Error("publishPack failed");
  return await res.json();
}

export async function createLearner(token, learnerId, displayName) {
  const res = await fetch(`${API}/learners`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ learner_id: learnerId, display_name: displayName })
  });
  if (!res.ok) throw new Error("createLearner failed");
  return await res.json();
}

export async function listLearners(token) {
  const res = await fetch(`${API}/learners`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listLearners failed");
  return await res.json();
}

export async function fetchLearnerState(token, learnerId) {
  const res = await fetch(`${API}/learners/${learnerId}/state`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("fetchLearnerState failed");
  return await res.json();
}

export async function fetchRecommendations(token, learnerId, packId) {
  const res = await fetch(`${API}/learners/${learnerId}/recommendations/${packId}`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("fetchRecommendations failed");
  return await res.json();
}

export async function postEvidence(token, learnerId, event) {
  const res = await fetch(`${API}/learners/${learnerId}/evidence`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(event)
  });
  if (!res.ok) throw new Error("postEvidence failed");
  return await res.json();
}

export async function submitEvaluatorJob(token, learnerId, payload) {
  const res = await fetch(`${API}/learners/${learnerId}/evaluator-jobs`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("submitEvaluatorJob failed");
  return await res.json();
}

export async function fetchEvaluatorHistory(token, learnerId) {
  const res = await fetch(`${API}/learners/${learnerId}/evaluator-history`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("fetchEvaluatorHistory failed");
  return await res.json();
}
