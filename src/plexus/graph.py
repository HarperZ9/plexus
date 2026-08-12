"""graph.py — render the mesh as a diagram (Mermaid / Graphviz DOT).

Discovery is only useful if you can see it. This turns the mesh into a picture:
organs as nodes, capability-labeled edges as producer -> consumer arrows, with
self-loops and the cross-tool wiring visible at a glance. Mermaid renders in any
Markdown viewer; DOT feeds Graphviz. Pure string output, zero deps.
"""
from __future__ import annotations

from collections import defaultdict

from .mesh import Mesh


_MERMAID_DIRECTIONS = frozenset({"TB", "TD", "BT", "RL", "LR"})
_MAX_GRAPH_TEXT_LENGTH = 4096


def _san(node: str) -> str:
    """A Mermaid/DOT-safe node id (organs are simple slugs already, but be safe)."""
    identifier = "".join(c if c.isalnum() else "_" for c in node)
    return "_end" if identifier == "end" else identifier


def _bounded(value: str, *, field: str) -> str:
    """Reject values whose escaping would make a graph output unbounded."""
    if not isinstance(value, str):
        raise ValueError(f"graph {field} must be a string")
    if len(value) > _MAX_GRAPH_TEXT_LENGTH:
        raise ValueError(f"graph {field} exceeds the {_MAX_GRAPH_TEXT_LENGTH}-character maximum")
    return value


def _node_ids(mesh: Mesh) -> dict[str, str]:
    """Assign deterministic, distinct Mermaid ids without changing unique slugs."""
    names = {_bounded(name, field="name") for name in mesh.organs}
    names.update(_bounded(edge.producer, field="name") for edge in mesh.edges)
    names.update(_bounded(edge.consumer, field="name") for edge in mesh.edges)
    groups: dict[str, list[str]] = defaultdict(list)
    for name in names:
        groups[_san(name) or "node"].append(name)

    ids, used_ids = {}, set()
    for name in sorted(names):
        base = _san(name) or "node"
        candidate = base if len(groups[base]) == 1 else f"{base}__{name.encode('utf-8', 'surrogatepass').hex()}"
        while candidate in names - {name} or candidate in used_ids:
            candidate = f"_{candidate}"
        ids[name] = candidate
        used_ids.add(candidate)
    return ids


def _escape_label(value: str, *, quote: str) -> str:
    """Escape graph string content so it remains inside one quoted label."""
    _bounded(value, field="label")
    escaped = []
    for char in value:
        code = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char == '"':
            escaped.append(quote)
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\r":
            escaped.append("\\r")
        elif char in {"\u2028", "\u2029"}:
            escaped.append(f"\\u{code:04x}")
        elif 0xD800 <= code <= 0xDFFF:
            escaped.append(f"\\u{code:04x}")
        elif code < 0x20 or 0x7F <= code <= 0x9F:
            escaped.append(f"\\x{code:02x}")
        else:
            escaped.append(char)
    return "".join(escaped)


def to_mermaid(mesh: Mesh, *, direction: str = "LR") -> str:
    """A Mermaid flowchart. Cross-tool edges are solid; self-loops dotted."""
    if not isinstance(direction, str) or direction not in _MERMAID_DIRECTIONS:
        raise ValueError("direction must be one of TB, TD, BT, RL, or LR")
    lines = [f"flowchart {direction}"]
    node_ids = _node_ids(mesh)
    for organ in mesh.organs:
        lines.append(f'  {node_ids[organ]}["{_escape_label(organ, quote="#quot;")}"]')
    for e in mesh.edges:
        arrow = "-.->" if e.self_loop else "-->"
        lines.append(
            f'  {node_ids[e.producer]} {arrow}|"{_escape_label(e.capability, quote="#quot;")}"| '
            f'{node_ids[e.consumer]}'
        )
    return "\n".join(lines)


def to_dot(mesh: Mesh) -> str:
    """A Graphviz DOT digraph."""
    lines = ["digraph plexus {", '  rankdir=LR;', '  node [shape=box];']
    for organ in mesh.organs:
        lines.append(f'  "{_escape_label(organ, quote="\\\"")}";')
    for e in mesh.edges:
        attrs = f'label="{_escape_label(e.capability, quote="\\\"")}"' + (", style=dotted" if e.self_loop else "")
        lines.append(
            f'  "{_escape_label(e.producer, quote="\\\"")}" -> "{_escape_label(e.consumer, quote="\\\"")}" [{attrs}];'
        )
    lines.append("}")
    return "\n".join(lines)
