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
export async function upsertPack(token, payload) { const res = await fetch(`${API}/packs`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("upsertPack failed"); return await res.json(); }
export async function createContribution(token, payload) { const res = await fetch(`${API}/contributions`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("createContribution failed"); return await res.json(); }
export async function fetchAdminPacks(token) { const res = await fetch(`${API}/admin/packs`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchAdminPacks failed"); return await res.json(); }
export async function fetchPackValidation(token, packId) { const res = await fetch(`${API}/admin/packs/${packId}/validation`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPackValidation failed"); return await res.json(); }
export async function fetchPackProvenance(token, packId) { const res = await fetch(`${API}/admin/packs/${packId}/provenance`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPackProvenance failed"); return await res.json(); }
export async function fetchPackVersions(token, packId) { const res = await fetch(`${API}/admin/packs/${packId}/versions`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPackVersions failed"); return await res.json(); }
export async function fetchPackComments(token, packId) { const res = await fetch(`${API}/admin/packs/${packId}/comments`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPackComments failed"); return await res.json(); }
export async function fetchSubmissions(token) { const res = await fetch(`${API}/admin/submissions`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchSubmissions failed"); return await res.json(); }
export async function fetchSubmissionDiff(token, submissionId) { const res = await fetch(`${API}/admin/submissions/${submissionId}/diff`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchSubmissionDiff failed"); return await res.json(); }
export async function fetchSubmissionGates(token, submissionId) { const res = await fetch(`${API}/admin/submissions/${submissionId}/gates`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchSubmissionGates failed"); return await res.json(); }
export async function fetchReviewTasks(token) { const res = await fetch(`${API}/admin/review-tasks`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchReviewTasks failed"); return await res.json(); }
export async function publishPack(token, packId, isPublished) { const res = await fetch(`${API}/admin/packs/${packId}/publish?is_published=${isPublished}`, { method: "POST", headers: authHeaders(token, false) }); if (!res.ok) throw new Error("publishPack failed"); return await res.json(); }
export async function fetchPublishability(token, packId) { const res = await fetch(`${API}/admin/packs/${packId}/publishability`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchPublishability failed"); return await res.json(); }
export async function governanceAction(token, packId, payload) { const res = await fetch(`${API}/admin/packs/${packId}/governance`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("governanceAction failed"); return await res.json(); }
export async function addReviewComment(token, packId, versionNumber, payload) { const res = await fetch(`${API}/admin/packs/${packId}/comments?version_number=${versionNumber}`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("addReviewComment failed"); return await res.json(); }
