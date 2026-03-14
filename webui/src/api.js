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
export async function editPatch(token, patchId, payload) {
  const res = await fetch(`${API}/pack-patches/${patchId}/edit`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("editPatch failed");
  return await res.json();
}
export async function applyPatch(token, patchId, payload) {
  const res = await fetch(`${API}/pack-patches/${patchId}/apply`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("applyPatch failed");
  return await res.json();
}
export async function editCurriculum(token, draftId, payload) {
  const res = await fetch(`${API}/curriculum-drafts/${draftId}/edit`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("editCurriculum failed");
  return await res.json();
}
export async function editSkill(token, bundleId, payload) {
  const res = await fetch(`${API}/skill-bundles/${bundleId}/edit`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("editSkill failed");
  return await res.json();
}
export async function listVersions(token, objectKind, objectId) {
  const res = await fetch(`${API}/object-versions/${objectKind}/${objectId}`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("listVersions failed");
  return await res.json();
}
export async function exportCurriculum(token, draftId) {
  const res = await fetch(`${API}/curriculum-drafts/${draftId}/export`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("exportCurriculum failed");
  return await res.json();
}
export async function exportSkill(token, bundleId) {
  const res = await fetch(`${API}/skill-bundles/${bundleId}/export`, { headers: authHeaders(token, false) });
  if (!res.ok) throw new Error("exportSkill failed");
  return await res.json();
}
