# Changelog

## 0.2.0

- Graph export (`to_mermaid`, `to_dot`; `plexus graph --format mermaid|dot`):
  render the mesh as a diagram, self-loops marked distinctly.
- Pipeline runner (`pipeline_script`; `plexus run --goal ORGAN`): turn a plan
  into a runnable, ordered shell script that ends at the target, with feedback
  loops surfaced as a comment.
- `COMPARISON.md`: grounded positioning vs MCP / LangGraph / Dagster / CrewAI —
  where plexus wins (decentralized, evidence-cited discovery) and where it does
  not (no execution engine).
- 22 falsifiers total.

## 0.1.0

Initial release.

- Manifest model (`Manifest`, `Port`) + validator: a tool's interop contract as
  plain JSON, with `consumable_as` aliasing and per-port module evidence.
- Mesh discovery (`discover`, `Mesh`): producer→consumer edges by capability,
  with self-loop marking and an `orphans()` honesty surface (unmet inputs /
  unconsumed outputs).
- Planning (`plan_to`, `route`): upstream pipeline to feed a target (Kahn
  ordering with feedback loops reported in `cyclic`), and shortest capability
  path between two tools.
- Built-in registry: five flagship manifests (gather, crucible, forum, index,
  mneme) grounded in a real 2026-07-07 source survey; external manifests via
  `load_dir` over `*.interop.json`.
- CLI: `discover`, `wiring`, `plan`, `route`, `validate`.
- 17 falsifiers; zero runtime dependencies.
