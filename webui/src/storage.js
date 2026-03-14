const KEY_PREFIX = "didactopus:learner-state:";

export function loadLearnerState(domainId) {
  const raw = localStorage.getItem(KEY_PREFIX + domainId);
  if (!raw) {
    return { learner_id: `learner-${domainId}`, records: [], history: [] };
  }
  try {
    return JSON.parse(raw);
  } catch {
    return { learner_id: `learner-${domainId}`, records: [], history: [] };
  }
}

export function saveLearnerState(domainId, state) {
  localStorage.setItem(KEY_PREFIX + domainId, JSON.stringify(state));
}

export function resetLearnerState(domainId) {
  localStorage.removeItem(KEY_PREFIX + domainId);
}
