const API = "http://127.0.0.1:8011/api";

export async function fetchPacks() {
  const res = await fetch(`${API}/packs`);
  return await res.json();
}

export async function fetchLearnerState(learnerId) {
  const res = await fetch(`${API}/learners/${learnerId}/state`);
  return await res.json();
}

export async function postEvidence(learnerId, event) {
  const res = await fetch(`${API}/learners/${learnerId}/evidence`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(event)
  });
  return await res.json();
}

export async function fetchRecommendations(learnerId, packId) {
  const res = await fetch(`${API}/learners/${learnerId}/recommendations/${packId}`);
  return await res.json();
}
