"""graph.py — render the mesh as a diagram (Mermaid / Graphviz DOT).

Discovery is only useful if you can see it. This turns the mesh into a picture:
organs as nodes, capability-labeled edges as producer -> consumer arrows, with
self-loops and the cross-tool wiring visible at a glance. Mermaid renders in any
Markdown viewer; DOT feeds Graphviz. Pure string output, zero deps.
"""
from __future__ import annotations

from collections import defaultdict

from .mesh import Mesh


def _san(node: str) -> str:
    """A Mermaid/DOT-safe node id (organs are simple slugs already, but be safe)."""
    return "".join(c if c.isalnum() else "_" for c in node)


def _node_ids(mesh: Mesh) -> dict[str, str]:
    """Assign deterministic, distinct Mermaid ids without changing unique slugs."""
    names = set(mesh.organs)
    names.update(edge.producer for edge in mesh.edges)
    names.update(edge.consumer for edge in mesh.edges)
    groups: dict[str, list[str]] = defaultdict(list)
    for name in names:
        groups[_san(name) or "node"].append(name)

    ids = {}
    for base, names in groups.items():
        if len(names) == 1:
            ids[names[0]] = base
        else:
            for name in names:
                ids[name] = f"{base}__{name.encode('utf-8', 'surrogatepass').hex()}"
    return ids


def _escape_label(value: str) -> str:
    """Escape graph string content so it remains inside one quoted label."""
    escaped = []
    for char in value:
        code = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char == '"':
            escaped.append('\\"')
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\r":
            escaped.append("\\r")
        elif code < 0x20 or 0x7F <= code <= 0x9F:
            escaped.append(f"\\x{code:02x}")
        else:
            escaped.append(char)
    return "".join(escaped)


def to_mermaid(mesh: Mesh, *, direction: str = "LR") -> str:
    """A Mermaid flowchart. Cross-tool edges are solid; self-loops dotted."""
    lines = [f"flowchart {direction}"]
    node_ids = _node_ids(mesh)
    for organ in mesh.organs:
        lines.append(f'  {node_ids[organ]}["{_escape_label(organ)}"]')
    for e in mesh.edges:
        arrow = "-.->" if e.self_loop else "-->"
        lines.append(
            f'  {node_ids[e.producer]} {arrow}|"{_escape_label(e.capability)}"| '
            f'{node_ids[e.consumer]}'
        )
    return "\n".join(lines)


def to_dot(mesh: Mesh) -> str:
    """A Graphviz DOT digraph."""
    lines = ["digraph plexus {", '  rankdir=LR;', '  node [shape=box];']
    for organ in mesh.organs:
        lines.append(f'  "{_escape_label(organ)}";')
    for e in mesh.edges:
        attrs = f'label="{_escape_label(e.capability)}"' + (", style=dotted" if e.self_loop else "")
        lines.append(
            f'  "{_escape_label(e.producer)}" -> "{_escape_label(e.consumer)}" [{attrs}];'
        )
    lines.append("}")
    return "\n".join(lines)
