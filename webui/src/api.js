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
export async function fetchDeploymentPolicy(token) { const res = await fetch(`${API}/deployment-policy`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchDeploymentPolicy failed"); return await res.json(); }
export async function fetchAgentCapabilities(token) { const res = await fetch(`${API}/agent/capabilities`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("fetchAgentCapabilities failed"); return await res.json(); }
export async function listServiceAccounts(token) { const res = await fetch(`${API}/admin/service-accounts`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("listServiceAccounts failed"); return await res.json(); }
export async function createServiceAccount(token, payload) { const res = await fetch(`${API}/admin/service-accounts`, { method: "POST", headers: authHeaders(token), body: JSON.stringify(payload) }); if (!res.ok) throw new Error("createServiceAccount failed"); return await res.json(); }
export async function rotateServiceAccount(token, name) { const res = await fetch(`${API}/admin/service-accounts/rotate`, { method: "POST", headers: authHeaders(token), body: JSON.stringify({ name }) }); if (!res.ok) throw new Error("rotateServiceAccount failed"); return await res.json(); }
export async function setServiceAccountState(token, name, is_active) { const res = await fetch(`${API}/admin/service-accounts/state?name=${encodeURIComponent(name)}`, { method: "POST", headers: authHeaders(token), body: JSON.stringify({ is_active }) }); if (!res.ok) throw new Error("setServiceAccountState failed"); return await res.json(); }
export async function listAgentAuditLogs(token) { const res = await fetch(`${API}/admin/agent-audit-logs`, { headers: authHeaders(token, false) }); if (!res.ok) throw new Error("listAgentAuditLogs failed"); return await res.json(); }
