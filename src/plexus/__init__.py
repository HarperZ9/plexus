"""plexus — capability discovery + auto-wiring for agent toolchains.

Point it at a set of tools that ship interop manifests and it discovers what each
one emits and consumes, then wires producer to consumer into a runnable pipeline
— every edge carrying the module that justifies it. Zero runtime dependencies.
"""
from .graph import to_dot, to_mermaid
from .manifest import Manifest, Port, validate
from .mesh import Edge, Mesh, discover
from .plan import plan_to, route
from .registry import builtin_manifests, load_dir
from .run import pipeline_script

__version__ = "0.2.0"

__all__ = [
    "Manifest", "Port", "validate",
    "Mesh", "Edge", "discover",
    "plan_to", "route",
    "to_mermaid", "to_dot", "pipeline_script",
    "builtin_manifests", "load_dir",
    "__version__",
]
