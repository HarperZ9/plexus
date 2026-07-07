"""mcp.py — a zero-dep MCP server so any agent can query the mesh live.

A CLI mesh is useful to a human; an agent needs it mid-task. This exposes
discover / wiring / plan / route as MCP tools over stdio JSON-RPC 2.0 (the same
shape every flagship speaks), so a harness can ask "what feeds crucible?" or
"how do gather and crucible connect?" while it works. No SDK, stdlib only.

The transport (`serve`) is a thin loop; all logic is in `handle`, which maps a
request dict to a response dict and is fully testable without any pipes.
"""
from __future__ import annotations

import json
import sys

from . import __version__
from .mesh import discover
from .plan import plan_to, route
from .registry import builtin_manifests, load_dir

PROTOCOL = "2025-06-18"

_DIR = {"dir": {"type": "string", "description": "load extra *.interop.json manifests from here"}}

TOOLS = [
    {"name": "plexus_discover",
     "description": "Discover the interop mesh: organs, producer->consumer edges (each with the module that produces it), and orphans (unmet inputs / unconsumed outputs).",
     "inputSchema": {"type": "object", "properties": dict(_DIR)}},
    {"name": "plexus_wiring",
     "description": "The wiring map: capability -> list of (producer, consumer) pairs.",
     "inputSchema": {"type": "object", "properties": dict(_DIR)}},
    {"name": "plexus_plan",
     "description": "The upstream pipeline that feeds a target organ, in dependency order, with any feedback loops reported.",
     "inputSchema": {"type": "object", "required": ["goal"],
                     "properties": {"goal": {"type": "string", "description": "organ to feed"}, **_DIR}}},
    {"name": "plexus_route",
     "description": "The shortest capability path from one organ to another.",
     "inputSchema": {"type": "object", "required": ["source", "target"],
                     "properties": {"source": {"type": "string"}, "target": {"type": "string"}, **_DIR}}},
]


def _mesh(args: dict):
    mans = list(builtin_manifests())
    if args.get("dir"):
        mans += load_dir(args["dir"])
    return discover(mans)


def _mesh_json(mesh) -> dict:
    return {"organs": mesh.organs,
            "edges": [{"producer": e.producer, "consumer": e.consumer,
                       "capability": e.capability, "self_loop": e.self_loop,
                       "via": e.producer_module} for e in mesh.edges],
            "orphans": mesh.orphans()}


def _call(params: dict) -> dict:
    name, args = params.get("name"), params.get("arguments", {}) or {}
    try:
        mesh = _mesh(args)
        if name == "plexus_discover":
            result = _mesh_json(mesh)
        elif name == "plexus_wiring":
            result = mesh.wiring()
        elif name == "plexus_plan":
            result = plan_to(mesh, args.get("goal", ""))
        elif name == "plexus_route":
            result = route(mesh, args.get("source", ""), args.get("target", ""))
        else:
            return {"content": [{"type": "text", "text": f"unknown tool {name!r}"}], "isError": True}
    except Exception as e:                       # a tool error is a result, not a crash
        return {"content": [{"type": "text", "text": f"[error] {type(e).__name__}: {e}"}],
                "isError": True}
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def _ok(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _err(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def handle(req: dict):
    """Map one JSON-RPC request to a response dict (or None for notifications)."""
    method, rid = req.get("method"), req.get("id")
    if method == "initialize":
        return _ok(rid, {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                         "serverInfo": {"name": "plexus", "version": __version__}})
    if method == "tools/list":
        return _ok(rid, {"tools": TOOLS})
    if method == "tools/call":
        return _ok(rid, _call(req.get("params", {})))
    if rid is None:                              # a notification (e.g. initialized)
        return None
    return _err(rid, -32601, f"method not found: {method}")


def serve(stdin=None, stdout=None) -> int:
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
