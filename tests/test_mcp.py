from __future__ import annotations

from didactopus.mcp import handle_request


def test_mcp_lists_tools() -> None:
    response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {tool["name"] for tool in response["result"]["tools"]}
    assert {
        "validate_pack",
        "sequence_plan",
        "citegeist_okf_source_corpus",
        "interoperability_registry",
        "validate_pack_capsule",
    } <= names


def test_mcp_returns_interoperability_registry() -> None:
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "interoperability_registry", "arguments": {}},
        }
    )
    text = response["result"]["content"][0]["text"]
    assert "didactopus" in text.lower()


def test_mcp_reports_unknown_tool() -> None:
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "missing", "arguments": {}},
        }
    )
    assert response["error"]["code"] == -32000
    assert "Unknown tool" in response["error"]["message"]
