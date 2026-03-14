from __future__ import annotations
from collections import defaultdict, deque
from .pack_validator import load_pack_artifacts

def graph_qa_for_pack(source_dir) -> dict:
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {"warnings": [], "summary": {"graph_warning_count": 0}}
    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    concept_ids = [c.get("id") for c in concepts if c.get("id")]
    prereqs = {c.get("id"): list(c.get("prerequisites", []) or []) for c in concepts if c.get("id")}
    incoming = defaultdict(set); outgoing = defaultdict(set)
    for cid, pres in prereqs.items():
        for p in pres:
            outgoing[p].add(cid); incoming[cid].add(p)
    warnings = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cid: WHITE for cid in concept_ids}; stack = []; found_cycles = []
    def dfs(node):
        color[node] = GRAY; stack.append(node)
        for nxt in outgoing.get(node, []):
            if color.get(nxt, WHITE) == WHITE: dfs(nxt)
            elif color.get(nxt) == GRAY and nxt in stack:
                idx = stack.index(nxt); found_cycles.append(stack[idx:] + [nxt])
        stack.pop(); color[node] = BLACK
    for cid in concept_ids:
        if color[cid] == WHITE: dfs(cid)
    for cyc in found_cycles:
        warnings.append("Prerequisite cycle detected: " + " -> ".join(cyc))
    for cid in concept_ids:
        if len(incoming[cid]) == 0 and len(outgoing[cid]) == 0:
            warnings.append(f"Concept '{cid}' is isolated from the prerequisite graph.")
    for cid in concept_ids:
        if len(outgoing[cid]) >= 3:
            warnings.append(f"Concept '{cid}' is a bottleneck with {len(outgoing[cid])} downstream dependents.")
    edge_count = sum(len(v) for v in prereqs.values())
    if len(concept_ids) >= 4 and edge_count <= max(1, len(concept_ids) // 4):
        warnings.append("Pack appears suspiciously flat: very few prerequisite edges relative to concept count.")
    indegree = {cid: len(incoming[cid]) for cid in concept_ids}
    q = deque([cid for cid in concept_ids if indegree[cid] == 0]); longest = {cid: 1 for cid in concept_ids}
    while q:
        node = q.popleft()
        for nxt in outgoing.get(node, []):
            longest[nxt] = max(longest.get(nxt, 1), longest[node] + 1)
            indegree[nxt] -= 1
            if indegree[nxt] == 0: q.append(nxt)
    max_chain = max(longest.values()) if longest else 0
    if max_chain >= 6:
        warnings.append(f"Pack has a deep prerequisite chain of length {max_chain}, which may indicate over-fragmentation.")
    summary = {"graph_warning_count": len(warnings), "concept_count": len(concept_ids), "edge_count": edge_count, "max_chain_length": max_chain}
    return {"warnings": warnings, "summary": summary}
