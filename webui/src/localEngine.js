export function getRecord(state, conceptId, dimension = "mastery") {
  return state.records.find((r) => r.concept_id === conceptId && r.dimension === dimension) || null;
}

export function conceptStatus(state, concept, minScore = 0.65, minConfidence = 0.45) {
  const rec = getRecord(state, concept.id, concept.masteryDimension || "mastery");
  if (rec && rec.score >= minScore && rec.confidence >= minConfidence) return "mastered";
  const prereqsOk = (concept.prerequisites || []).every((pid) => {
    const p = getRecord(state, pid, concept.masteryDimension || "mastery");
    return p && p.score >= minScore && p.confidence >= minConfidence;
  });
  if (prereqsOk) return rec ? "active" : "available";
  return "locked";
}

export function buildMasteryMap(state, domain) {
  return domain.concepts.map((c) => ({ id: c.id, label: c.title, status: conceptStatus(state, c) }));
}

export function progressPercent(state, domain) {
  const total = Math.max(1, domain.concepts.length);
  const mastered = domain.concepts.filter((c) => conceptStatus(state, c) === "mastered").length;
  return Math.round((mastered / total) * 100);
}

export function milestoneMessages(state, domain) {
  const msgs = [];
  for (const concept of domain.concepts) {
    if (conceptStatus(state, concept) === "mastered") msgs.push(`${concept.title} mastered`);
  }
  if (msgs.length === 0) msgs.push("Complete your first guided exercise to earn a visible mastery marker");
  return msgs;
}

export function claimReadiness(state, domain, minScore = 0.75, minConfidence = 0.60) {
  const records = domain.concepts
    .map((c) => getRecord(state, c.id, c.masteryDimension || "mastery"))
    .filter(Boolean);
  const mastered = records.filter((r) => r.score >= minScore && r.confidence >= minConfidence).length;
  const avgScore = records.length ? records.reduce((a, r) => a + r.score, 0) / records.length : 0;
  const avgConfidence = records.length ? records.reduce((a, r) => a + r.confidence, 0) / records.length : 0;
  return {
    ready: mastered >= Math.max(1, domain.concepts.length - 1) && avgScore >= minScore && avgConfidence >= minConfidence,
    mastered,
    avgScore,
    avgConfidence
  };
}
