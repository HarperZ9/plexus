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
from .manifest import duplicate_organs, validate
from .mesh import discover
from .plan import plan_to, route
from .registry import builtin_manifests, load_dir


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
                   "via": e.producer_module, "evidence": e.evidence}
                  for e in mesh.edges],
        "orphans": mesh.orphans(),
        "collisions": mesh.collisions,
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

    args = ap.parse_args(argv)
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
    if args.cmd == "validate":
        problems = {m.organ: validate(m) for m in mans}
        report = {k: v for k, v in problems.items() if v}
        dups = duplicate_organs(mans)
        if dups:
            # A set-level clash the per-organ dict above cannot show (its own key
            # collapses the duplicates); name it so a collision can never launder
            # to {"ok": true}.
            report["duplicate_organs"] = dups
        print(json.dumps(report or {"ok": True}, indent=2))
        return 1 if report else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
