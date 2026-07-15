"""manifest.py — what a tool declares about how it plugs into others.

A manifest is a tool's interop contract: the capabilities it EMITS (re-checkable
artifacts another tool could consume) and the capabilities it CONSUMES (inputs it
accepts). A capability is a stable string: a schema id like
"mneme.crucible-export/1" or a shared-spine kind like
"project-telos.flagship-action/v1". Matching is by capability string, so an edge
forms when a producer DECLARES a capability the consumer DECLARES it accepts.

Every port carries `module` (a file:function pointer) the producer names as the
source. plexus does not import, resolve, or run that pointer, so the mesh is
DECLARED, not probed: the module is a self-reported citation to follow, not a
verified receipt. A manifest is a plain dict/JSON, so any tool in any language
can ship one; nothing here imports the tools it describes.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Port:
    """One capability a tool emits or consumes."""
    capability: str                 # the match key (schema id or shared kind)
    title: str = ""                 # human label
    module: str = ""                # evidence: repo-relative file:function
    summary: str = ""
    consumable_as: tuple = ()       # extra capabilities an EMIT also satisfies
                                    # (e.g. mneme.crucible-export/1 -> crucible.thesis)

    def satisfies(self, capability: str) -> bool:
        return capability == self.capability or capability in self.consumable_as


@dataclass
class Manifest:
    organ: str
    invoke: dict = field(default_factory=dict)   # {cli, mcp_server, python_import}
    emits: list = field(default_factory=list)    # list[Port]
    consumes: list = field(default_factory=list)  # list[Port]
    evidence: list = field(default_factory=list)  # file paths the manifest was grounded on

    @staticmethod
    def from_dict(d: dict) -> "Manifest":
        def ports(key):
            out = []
            for p in d.get(key, []):
                if isinstance(p, str):
                    out.append(Port(capability=p))
                elif isinstance(p, dict):
                    out.append(Port(
                        capability=p["capability"], title=p.get("title", ""),
                        module=p.get("module", ""), summary=p.get("summary", ""),
                        consumable_as=tuple(p.get("consumable_as", ()))))
            return out
        return Manifest(organ=d["organ"], invoke=d.get("invoke", {}),
                        emits=ports("emits"), consumes=ports("consumes"),
                        evidence=list(d.get("evidence", [])))

    def to_dict(self) -> dict:
        def dump(ports):
            return [{"capability": p.capability, "title": p.title, "module": p.module,
                     "summary": p.summary, "consumable_as": list(p.consumable_as)}
                    for p in ports]
        return {"organ": self.organ, "invoke": self.invoke,
                "emits": dump(self.emits), "consumes": dump(self.consumes),
                "evidence": self.evidence}


def validate(m) -> list:
    """Problems with a manifest (empty list == valid). A validator reports
    malformed input; it never raises on it."""
    issues = []
    if not isinstance(m, Manifest):
        return ["not a Manifest"]
    if not m.organ or not isinstance(m.organ, str):
        issues.append("organ id missing or not a string")
    seen = set()
    for side in ("emits", "consumes"):
        for i, p in enumerate(getattr(m, side)):
            if not isinstance(p, Port) or not p.capability:
                issues.append(f"{side}[{i}] has no capability")
                continue
            key = (side, p.capability)
            if key in seen:
                issues.append(f"{side} declares {p.capability!r} twice")
            seen.add(key)
    return issues
