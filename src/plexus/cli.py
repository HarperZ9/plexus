"""cli.py — plexus command line.

  plexus discover [--builtin] [--dir DIR]   # the mesh: organs, edges, orphans
  plexus wiring   [...]                      # capability -> (producer, consumer) pairs
  plexus plan --goal ORGAN [...]             # upstream pipeline that feeds ORGAN
  plexus route --from A --to B [...]         # capability path from A to B
  plexus validate [...]                      # manifest problems (exit 1 if any)
"""
from __future__ import annotations

import argparse
import json

from . import __version__
from .graph import to_dot, to_mermaid
from .manifest import validate
from .mesh import discover
from .plan import plan_to, route
from .registry import builtin_manifests, export_all, load_dir
from .run import pipeline_script


def _load(args) -> list:
    mans = list(builtin_manifests()) if (args.builtin or not args.dir) else []
    if args.dir:
        mans += load_dir(args.dir)
    return mans


def _mesh_json(mesh) -> dict:
    return {
        "organs": mesh.organs,
        "edges": [{"producer": e.producer, "consumer": e.consumer,
                   "capability": e.capability, "self_loop": e.self_loop,
                   "via": e.producer_module} for e in mesh.edges],
        "orphans": mesh.orphans(),
    }


def _add_source_flags(p):
    p.add_argument("--builtin", action="store_true", help="include the built-in flagship manifests")
    p.add_argument("--dir", default="", help="load *.interop.json manifests from this directory")


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(prog="plexus", description=__doc__)
    ap.add_argument("--version", action="version", version=f"plexus {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("discover", "wiring", "validate"):
        sp = sub.add_parser(name)
        _add_source_flags(sp)
    pp = sub.add_parser("plan"); _add_source_flags(pp)
    pp.add_argument("--goal", required=True, help="organ you want to feed")
    rp = sub.add_parser("route"); _add_source_flags(rp)
    rp.add_argument("--from", dest="src", required=True)
    rp.add_argument("--to", dest="dst", required=True)
    gp = sub.add_parser("graph"); _add_source_flags(gp)
    gp.add_argument("--format", default="mermaid", choices=["mermaid", "dot"])
    up = sub.add_parser("run"); _add_source_flags(up)
    up.add_argument("--goal", required=True, help="organ you want to feed")
    ep = sub.add_parser("export")
    ep.add_argument("--dir", default="manifests", help="write <organ>.interop.json files here")
    sub.add_parser("mcp")   # stdio MCP server: discover/wiring/plan/route as tools

    args = ap.parse_args(argv)

    if args.cmd == "mcp":
        from .mcp import serve
        return serve()
    if args.cmd == "export":
        print("\n".join(export_all(args.dir)))
        return 0

    mans = _load(args)

    if args.cmd == "discover":
        print(json.dumps(_mesh_json(discover(mans)), indent=2))
        return 0
    if args.cmd == "wiring":
        print(json.dumps(discover(mans).wiring(), indent=2))
        return 0
    if args.cmd == "plan":
        print(json.dumps(plan_to(discover(mans), args.goal), indent=2))
        return 0
    if args.cmd == "route":
        print(json.dumps(route(discover(mans), args.src, args.dst), indent=2))
        return 0
    if args.cmd == "graph":
        mesh = discover(mans)
        print(to_mermaid(mesh) if args.format == "mermaid" else to_dot(mesh))
        return 0
    if args.cmd == "run":
        print(pipeline_script(discover(mans), args.goal))
        return 0
    if args.cmd == "validate":
        problems = {m.organ: validate(m) for m in mans}
        problems = {k: v for k, v in problems.items() if v}
        print(json.dumps(problems or {"ok": True}, indent=2))
        return 1 if problems else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
