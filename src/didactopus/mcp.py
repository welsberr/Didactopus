from __future__ import annotations

import json
import sys
from typing import Any, Callable

from .citegeist_okf import write_citegeist_okf_source_bundle
from .interoperability import registry_payload, validate_pack_capsule
from .notebook_learning_sequence import build_notebook_sequence_session_plan
from .pack_validator import validate_pack_directory


SERVER_INFO = {"name": "didactopus-mcp", "version": "0.1.0"}


def _json_text(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}


def _validate_pack(arguments: dict[str, Any]) -> dict[str, Any]:
    return _json_text(validate_pack_directory(arguments["source_dir"]))


def _sequence_plan(arguments: dict[str, Any]) -> dict[str, Any]:
    return _json_text(
        build_notebook_sequence_session_plan(
            arguments["sequence"],
            learner_goal=arguments.get("learner_goal"),
        )
    )


def _citegeist_okf_source_corpus(arguments: dict[str, Any]) -> dict[str, Any]:
    return _json_text(write_citegeist_okf_source_bundle(arguments["bundle_dir"], arguments["out_dir"]))


def _interoperability_registry(arguments: dict[str, Any]) -> dict[str, Any]:
    return _json_text(registry_payload())


def _validate_pack_capsule(arguments: dict[str, Any]) -> dict[str, Any]:
    return _json_text(validate_pack_capsule(arguments["manifest"]))


TOOLS: dict[str, dict[str, Any]] = {
    "validate_pack": {
        "description": "Validate a Didactopus pack directory.",
        "inputSchema": {
            "type": "object",
            "properties": {"source_dir": {"type": "string"}},
            "required": ["source_dir"],
        },
        "handler": _validate_pack,
    },
    "sequence_plan": {
        "description": "Build a mentorship-oriented plan from a Notebook Didactopus sequence JSON file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sequence": {"type": "string"},
                "learner_goal": {"type": "string"},
            },
            "required": ["sequence"],
        },
        "handler": _sequence_plan,
    },
    "citegeist_okf_source_corpus": {
        "description": "Convert a CiteGeist OKF bundle into Didactopus source-corpus artifacts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_dir": {"type": "string"},
                "out_dir": {"type": "string"},
            },
            "required": ["bundle_dir", "out_dir"],
        },
        "handler": _citegeist_okf_source_corpus,
    },
    "interoperability_registry": {
        "description": "Return the Didactopus standards registry and object crosswalk.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": _interoperability_registry,
    },
    "validate_pack_capsule": {
        "description": "Validate a didactopus-pack-capsule manifest JSON file.",
        "inputSchema": {
            "type": "object",
            "properties": {"manifest": {"type": "string"}},
            "required": ["manifest"],
        },
        "handler": _validate_pack_capsule,
    },
}


def list_tools() -> list[dict[str, Any]]:
    return [
        {key: value for key, value in tool.items() if key != "handler"} | {"name": name}
        for name, tool in TOOLS.items()
    ]


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}
    try:
        if method == "initialize":
            result = {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            }
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            result = {"tools": list_tools()}
        elif method == "tools/call":
            name = params.get("name")
            tool = TOOLS.get(name)
            if tool is None:
                raise ValueError(f"Unknown tool: {name}")
            handler: Callable[[dict[str, Any]], dict[str, Any]] = tool["handler"]
            result = handler(params.get("arguments") or {})
        else:
            raise ValueError(f"Unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(exc)},
        }


def serve(input_stream=sys.stdin, output_stream=sys.stdout) -> None:
    for line in input_stream:
        if not line.strip():
            continue
        response = handle_request(json.loads(line))
        if response is not None:
            output_stream.write(json.dumps(response) + "\n")
            output_stream.flush()


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
