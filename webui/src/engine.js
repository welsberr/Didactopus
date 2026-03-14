export function cloneState(obj) {
  return JSON.parse(JSON.stringify(obj));
}

export function getRecord(state, conceptId, dimension = "mastery") {
  return state.records.find((r) => r.concept_id === conceptId && r.dimension === dimension) || null;
}

export function applyEvidence(state, event, decay = 0.05, reinforcement = 0.25) {
  const next = cloneState(state);
  let rec = getRecord(next, event.concept_id, event.dimension);
  if (!rec) {
    rec = {
      concept_id: event.concept_id,
      dimension: event.dimension,
      score: 0,
      confidence: 0,
      evidence_count: 0,
      last_updated: event.timestamp
    };
    next.records.push(rec);
  }

  const weight = Math.max(0.05, Math.min(1.0, event.confidence_hint ?? 0.5));
  rec.score = ((rec.score * rec.evidence_count) + (event.score * weight)) / Math.max(1, rec.evidence_count + 1);
  rec.confidence = Math.min(
    1.0,
    Math.max(0.0, rec.confidence * (1.0 - decay) + reinforcement * weight + 0.10 * Math.max(0.0, Math.min(1.0, event.score)))
  );
  rec.evidence_count += 1;
  rec.last_updated = event.timestamp;
  next.history.push(event);
  return next;
}

export function prereqsSatisfied(state, concept, minScore = 0.65, minConfidence = 0.45) {
  return (concept.prerequisites || []).every((pid) => {
    const rec = getRecord(state, pid, concept.masteryDimension || "mastery");
    return rec && rec.score >= minScore && rec.confidence >= minConfidence;
  });
}

export function conceptStatus(state, concept, minScore = 0.65, minConfidence = 0.45) {
  const rec = getRecord(state, concept.id, concept.masteryDimension || "mastery");
  if (rec && rec.score >= minScore && rec.confidence >= minConfidence) return "mastered";
  if (prereqsSatisfied(state, concept, minScore, minConfidence)) return rec ? "active" : "available";
  return "locked";
}

export function buildMasteryMap(state, domain) {
  return domain.concepts.map((c) => ({
    id: c.id,
    label: c.title,
    status: conceptStatus(state, c)
  }));
}

export function progressPercent(state, domain) {
  const total = Math.max(1, domain.concepts.length);
  const mastered = domain.concepts.filter((c) => conceptStatus(state, c) === "mastered").length;
  return Math.round((mastered / total) * 100);
}

export function recommendNext(state, domain) {
  const cards = [];
  for (const concept of domain.concepts) {
    const status = conceptStatus(state, concept);
    const rec = getRecord(state, concept.id, concept.masteryDimension || "mastery");
    if (status === "available" || status === "active") {
      cards.push({
        id: concept.id,
        title: `Work on ${concept.title}`,
        minutes: status === "available" ? 15 : 10,
        reason: status === "available"
          ? "Prerequisites are satisfied, so this is the best next unlock."
          : "You have started this concept, but mastery is not yet secure.",
        why: [
          "Prerequisite check passed",
          rec ? `Current score: ${rec.score.toFixed(2)}` : "No evidence recorded yet",
          rec ? `Current confidence: ${rec.confidence.toFixed(2)}` : "Confidence starts after your first exercise"
        ],
        reward: concept.exerciseReward || `${concept.title} progress recorded`,
        conceptId: concept.id,
        scoreHint: status === "available" ? 0.82 : 0.76,
        confidenceHint: status === "available" ? 0.72 : 0.55
      });
    }
  }
  for (const rec of state.records) {
    if (rec.dimension === "mastery" && rec.confidence < 0.40) {
      const concept = domain.concepts.find((c) => c.id === rec.concept_id);
      if (concept) {
        cards.push({
          id: `${concept.id}-reinforce`,
          title: `Reinforce ${concept.title}`,
          minutes: 8,
          reason: "Your score is promising, but confidence is still thin.",
          why: [
            `Confidence ${rec.confidence.toFixed(2)} is below reinforcement threshold`,
            "A small fresh exercise can stabilize recall"
          ],
          reward: "Confidence ring grows",
          conceptId: concept.id,
          scoreHint: Math.max(0.60, rec.score),
          confidenceHint: 0.30
        });
      }
    }
  }
  return cards.slice(0, 4);
}

export function milestoneMessages(state, domain) {
  const msgs = [];
  for (const concept of domain.concepts) {
    const status = conceptStatus(state, concept);
    if (status === "mastered") msgs.push(`${concept.title} mastered`);
  }
  if (msgs.length === 0) msgs.push("Complete your first guided exercise to earn a visible mastery marker");
  return msgs;
}

export function claimReadiness(state, domain, minScore = 0.75, minConfidence = 0.60) {
  const mastered = domain.concepts.filter((c) => {
    const rec = getRecord(state, c.id, c.masteryDimension || "mastery");
    return rec && rec.score >= minScore && rec.confidence >= minConfidence;
  }).length;

  const records = domain.concepts.map((c) => getRecord(state, c.id, c.masteryDimension || "mastery")).filter(Boolean);
  const avgScore = records.length ? records.reduce((a, r) => a + r.score, 0) / records.length : 0;
  const avgConfidence = records.length ? records.reduce((a, r) => a + r.confidence, 0) / records.length : 0;

  return {
    ready: mastered >= Math.max(1, domain.concepts.length - 1) && avgScore >= minScore && avgConfidence >= minConfidence,
    mastered,
    avgScore,
    avgConfidence
  };
}
