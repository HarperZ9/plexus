"""Falsifiers for the MCP server (agent-consumable mesh over JSON-RPC).

Load-bearing: (1) initialize reports the plexus server; (2) tools/list advertises
the four mesh tools with schemas; (3) tools/call actually runs discovery/plan/
route and returns JSON content; (4) a bad tool or bad method is a typed error, not
a crash; (5) notifications get no response. All via handle() — no pipes needed.
"""
import io
import json

from plexus.mcp import handle, serve


def _req(method, rid=1, params=None):
    r = {"jsonrpc": "2.0", "method": method}
    if rid is not None:
        r["id"] = rid
    if params is not None:
        r["params"] = params
    return r


def test_initialize_reports_the_server():
    resp = handle(_req("initialize"))
    assert resp["result"]["serverInfo"]["name"] == "plexus"
    assert "protocolVersion" in resp["result"]


def test_tools_list_advertises_the_mesh_tools():
    tools = {t["name"] for t in handle(_req("tools/list"))["result"]["tools"]}
    assert tools == {"plexus_discover", "plexus_wiring", "plexus_plan", "plexus_route"}


def test_call_discover_returns_the_real_mesh():
    resp = handle(_req("tools/call", params={"name": "plexus_discover", "arguments": {}}))
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert set(payload["organs"]) == {"gather", "crucible", "forum", "index", "mneme"}
    assert any(e["producer"] == "mneme" and e["consumer"] == "crucible" for e in payload["edges"])


def test_call_plan_and_route():
    plan = json.loads(handle(_req("tools/call", params={
        "name": "plexus_plan", "arguments": {"goal": "crucible"}}))["result"]["content"][0]["text"])
    assert "gather" in plan["order"]
    rt = json.loads(handle(_req("tools/call", params={
        "name": "plexus_route", "arguments": {"source": "gather", "target": "crucible"}}))["result"]["content"][0]["text"])
    assert rt["connected"] is True


def test_unknown_tool_and_method_are_typed_not_crashes():
    bad_tool = handle(_req("tools/call", params={"name": "nope", "arguments": {}}))
    assert bad_tool["result"]["isError"] is True
    bad_method = handle(_req("frobnicate"))
    assert bad_method["error"]["code"] == -32601


def test_notification_gets_no_response():
    assert handle(_req("notifications/initialized", rid=None)) is None


def test_serve_loop_reads_and_writes_jsonrpc():
    stdin = io.StringIO(json.dumps(_req("initialize")) + "\n"
                        + json.dumps(_req("tools/list", rid=2)) + "\n")
    out = io.StringIO()
    serve(stdin=stdin, stdout=out)
    lines = [json.loads(x) for x in out.getvalue().splitlines() if x.strip()]
    assert lines[0]["result"]["serverInfo"]["name"] == "plexus"
    assert lines[1]["id"] == 2 and "tools" in lines[1]["result"]
