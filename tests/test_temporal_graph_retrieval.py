from __future__ import annotations

from didactopus.graph_retrieval import GraphBundle, temporal_claim_context, temporal_graph_slice, temporal_summary


def _bundle() -> GraphBundle:
    return GraphBundle(
        knowledge_graph={
            "graph_id": "detective-course",
            "title": "Detective Reasoning",
            "nodes": [
                {
                    "id": "claim::alibi",
                    "type": "claim",
                    "title": "The alibi holds",
                    "status": "promoted",
                    "introduced_at": "1900-01-01",
                },
                {
                    "id": "evidence::ticket",
                    "type": "evidence",
                    "title": "Ticket timestamp",
                    "available_at": "1901-01-01",
                },
                {
                    "id": "evidence::clock",
                    "type": "evidence",
                    "title": "Clock contradiction",
                    "available_at": "1902-01-01",
                },
            ],
            "edges": [
                {
                    "source": "evidence::ticket",
                    "target": "claim::alibi",
                    "type": "supports",
                    "available_at": "1901-01-01",
                },
                {
                    "source": "evidence::clock",
                    "target": "claim::alibi",
                    "type": "contradicts",
                    "available_at": "1902-01-01",
                },
            ],
        },
        source_corpus={"fragments": []},
    )


def test_temporal_graph_slice_filters_future_evidence() -> None:
    payload = temporal_graph_slice(_bundle(), "1901-06-01")

    assert {node["id"] for node in payload["nodes"]} == {"claim::alibi", "evidence::ticket"}
    assert payload["summary"]["edge_count"] == 1


def test_temporal_summary_reports_timeline_events_and_stale_claims() -> None:
    payload = temporal_summary(_bundle())

    assert payload["summary"]["timeline_event_count"] == 5
    assert payload["stale_claims"][0]["claim_id"] == "claim::alibi"


def test_temporal_claim_context_changes_status_by_time() -> None:
    early = temporal_claim_context(_bundle(), "claim::alibi", "1901-06-01")
    late = temporal_claim_context(_bundle(), "claim::alibi", "1902-06-01")

    assert early["status"]["status"] == "supported"
    assert late["status"]["status"] == "contradicted"
    assert late["tenability_window"]["tenable_until"] == "1902-01-01"
