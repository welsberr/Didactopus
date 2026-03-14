const API = "http://127.0.0.1:8011/api";

export async function login(username, password) {
  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error("Login failed");
  return await res.json();
}

function authHeaders(token) {
  return { "Content-Type": "application/json", "Authorization": `Bearer ${token}` };
}

export async function fetchPacks(token) {
  const res = await fetch(`${API}/packs`, { headers: authHeaders(token) });
  return await res.json();
}

export async function createLearner(token, learnerId, displayName) {
  const res = await fetch(`${API}/learners`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ learner_id: learnerId, display_name: displayName })
  });
  return await res.json();
}

export async function fetchLearnerState(token, learnerId) {
  const res = await fetch(`${API}/learners/${learnerId}/state`, { headers: authHeaders(token) });
  return await res.json();
}

export async function postEvidence(token, learnerId, event) {
  const res = await fetch(`${API}/learners/${learnerId}/evidence`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(event)
  });
  return await res.json();
}

export async function fetchRecommendations(token, learnerId, packId) {
  const res = await fetch(`${API}/learners/${learnerId}/recommendations/${packId}`, { headers: authHeaders(token) });
  return await res.json();
}

export async function submitEvaluatorJob(token, learnerId, payload) {
  const res = await fetch(`${API}/learners/${learnerId}/evaluator-jobs`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload)
  });
  return await res.json();
}

export async function fetchEvaluatorJob(token, jobId) {
  const res = await fetch(`${API}/evaluator-jobs/${jobId}`, { headers: authHeaders(token) });
  return await res.json();
}
