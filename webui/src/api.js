const API = "http://127.0.0.1:8011/api";

function authHeaders(token, json=true) {
  const h = { Authorization: `Bearer ${token}` };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export async function login(username, password) {
  const res = await fetch(`${API}/login`, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({ username, password })});
  if (!res.ok) throw new Error("login failed");
  return await res.json();
}
export async function listCandidates(token) {
  const res = await fetch(`${API}/knowledge-candidates`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listCandidates failed");
  return await res.json();
}
export async function createCandidate(token, payload) {
  const res = await fetch(`${API}/knowledge-candidates`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("createCandidate failed");
  return await res.json();
}
export async function promoteCandidate(token, candidateId, payload) {
  const res = await fetch(`${API}/knowledge-candidates/${candidateId}/promote`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("promoteCandidate failed");
  return await res.json();
}
export async function runSynthesis(token, payload) {
  const res = await fetch(`${API}/synthesis/run`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("runSynthesis failed");
  return await res.json();
}
export async function listSynthesisCandidates(token) {
  const res = await fetch(`${API}/synthesis/candidates`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listSynthesisCandidates failed");
  return await res.json();
}
export async function promoteSynthesis(token, synthesisId, payload) {
  const res = await fetch(`${API}/synthesis/candidates/${synthesisId}/promote`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("promoteSynthesis failed");
  return await res.json();
}
export async function listPackPatches(token) {
  const res = await fetch(`${API}/pack-patches`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listPackPatches failed");
  return await res.json();
}
export async function listCurriculumDrafts(token) {
  const res = await fetch(`${API}/curriculum-drafts`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listCurriculumDrafts failed");
  return await res.json();
}
export async function listSkillBundles(token) {
  const res = await fetch(`${API}/skill-bundles`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listSkillBundles failed");
  return await res.json();
}
