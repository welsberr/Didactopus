from __future__ import annotations
from collections import defaultdict
import networkx as nx
from .pack_validator import load_pack_artifacts, validate_pack_directory

def graph_qa_for_pack(source_dir) -> dict:
    validation = validate_pack_directory(source_dir)
    if not validation["ok"]:
        return {
            "status": "invalid_input",
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "summary": {
                "analysis_status": "not_run",
                "graph_warning_count": None,
                "validation_error_count": len(validation["errors"]),
            },
        }
    loaded = load_pack_artifacts(source_dir)
    if not loaded["ok"]:
        return {
            "status": "invalid_input",
            "errors": loaded["errors"],
            "warnings": loaded["warnings"],
            "summary": {"analysis_status": "not_run", "graph_warning_count": None},
        }

    concepts = loaded["artifacts"]["concepts"].get("concepts", []) or []
    concept_ids = [c.get("id") for c in concepts if c.get("id")]
    prereqs = {c.get("id"): list(c.get("prerequisites", []) or []) for c in concepts if c.get("id")}

    incoming = defaultdict(set)
    outgoing = defaultdict(set)
    errors = []
    concept_id_set = set(concept_ids)
    for cid, pres in prereqs.items():
        for p in pres:
            if p not in concept_id_set:
                errors.append(f"Concept '{cid}' references missing prerequisite concept id: {p}")
                continue
            outgoing[p].add(cid)
            incoming[cid].add(p)

    if errors:
        return {
            "status": "invalid_input",
            "errors": errors,
            "warnings": validation["warnings"],
            "summary": {
                "analysis_status": "not_run",
                "graph_warning_count": None,
                "validation_error_count": len(errors),
                "concept_count": len(concept_ids),
            },
        }

    warnings = list(validation["warnings"])

    # SCCs identify exact cycle members; DAG descendants are reported separately.
    graph = nx.DiGraph()
    graph.add_nodes_from(concept_ids)
    graph.add_edges_from((prereq, concept) for concept, prereqs_for_concept in prereqs.items() for prereq in prereqs_for_concept)
    cyclic_components = sorted(
        (sorted(component) for component in nx.strongly_connected_components(graph)
         if len(component) > 1 or any(graph.has_edge(node, node) for node in component)),
        key=lambda component: component,
    )
    cycle_members = {node for component in cyclic_components for node in component}
    blocked_members = set()
    for member in cycle_members:
        blocked_members.update(nx.descendants(graph, member))
    blocked_members.difference_update(cycle_members)
    for component in cyclic_components:
        warnings.append("Prerequisite cycle members: " + ", ".join(component))
    if blocked_members:
        warnings.append("Acyclic concepts downstream of prerequisite cycles: " + ", ".join(sorted(blocked_members)))

    # Isolated concepts
    for cid in concept_ids:
        if len(incoming[cid]) == 0 and len(outgoing[cid]) == 0:
            warnings.append(f"Concept '{cid}' is isolated from the prerequisite graph.")

    # Bottlenecks
    threshold = 3
    for cid in concept_ids:
        if len(outgoing[cid]) >= threshold:
            warnings.append(f"Concept '{cid}' has a high direct dependency count ({len(outgoing[cid])}). Review whether this prerequisite structure is intentional.")

    # Flatness
    edge_count = graph.number_of_edges()
    if len(concept_ids) >= 4 and edge_count <= max(1, len(concept_ids) // 4):
        warnings.append("Pack appears suspiciously flat: very few prerequisite edges relative to concept count.")

    # Deep chains
    max_chain = None
    if not cyclic_components:
        max_chain = max((len(path) for path in nx.dag_longest_path(graph, weight=None)), default=0)
    elif graph.number_of_nodes() == 0:
        max_chain = 0
    if max_chain is not None and max_chain >= 6:
        warnings.append(f"Pack has a deep prerequisite chain of length {max_chain}, which may indicate over-fragmentation.")

    summary = {
        "analysis_status": "complete",
        "graph_warning_count": len(warnings),
        "validation_error_count": 0,
        "concept_count": len(concept_ids),
        "edge_count": edge_count,
        "max_chain_length": max_chain,
        "cycle_count": len(cyclic_components),
        "cyclic_component_count": len(cyclic_components),
        "cycle_member_count": len(cycle_members),
        "blocked_cycle_node_count": len(blocked_members),
        "isolated_count": sum(1 for cid in concept_ids if len(incoming[cid]) == 0 and len(outgoing[cid]) == 0),
    }
    return {"status": "ok", "errors": [], "warnings": warnings, "cyclic_components": cyclic_components,
            "blocked_cycle_nodes": sorted(blocked_members), "summary": summary}
