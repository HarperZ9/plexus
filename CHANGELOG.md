# Changelog

## Unreleased

Honesty repairs to the wiring surface (the credo: color/verdict vocabulary only
where a real check ran; no receipt no accept; the honest null is first-class).

- Edges are DECLARED, not probed: plexus never imports, resolves, or runs the
  tools, so each edge is tagged `evidence: "declared"` and the "grounded, not
  asserted" / "traces back to real code" / "genuinely compose" wording is gone.
- Duplicate organ ids are NAMED (`discover().collisions`, `validate` reports
  `duplicate_organs` and exits 1) instead of collapsing last-writer-wins.
- `discover` stamps a re-runnable `receipt`: plexus version, UTC timestamp, and
  per-manifest source + sha256 over canonical content.
- `validate` now fails on an emit with no module evidence and never raises on a
  malformed external manifest (missing organ / capability).
- `plan_to` marks a hop `runnable: false` and names the absence instead of
  coercing an undeclared CLI into a command.
- Declare the schema-exact Mneme/Crucible replay loop:
  `crucible.replay-template/1` routes Crucible→Mneme and
  `crucible.replay-pack/1` routes Mneme→Crucible, while retaining the existing
  Mneme→Crucible thesis route.

## 0.2.0

- Graph export (`to_mermaid`, `to_dot`; `plexus graph --format mermaid|dot`):
  render the mesh as a diagram, self-loops marked distinctly.
- Pipeline runner (`pipeline_script`; `plexus run --goal ORGAN`): turn a plan
  into a runnable, ordered shell script that ends at the target, with feedback
  loops surfaced as a comment.
- `COMPARISON.md`: grounded positioning vs MCP / LangGraph / Dagster / CrewAI —
  where plexus wins (decentralized, evidence-cited discovery) and where it does
  not (no execution engine).
- Manifest export (`export_all`, `plexus export`): write each flagship's
  `<organ>.interop.json` — the exact file a tool ships to join the mesh. The
  five real manifests are committed under `manifests/`, and a round-trip test
  proves discovery from the JSON files matches the in-code registry exactly
  (the format is lossless — the premise of decentralized discovery).
- MCP server (`mcp.py`, `plexus mcp`): a zero-dep stdio JSON-RPC server exposing
  discover / wiring / plan / route as MCP tools, so an agent can query the mesh
  mid-task (not just a human at a CLI). `handle()` is transport-free and tested.
- 31 falsifiers total.

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
  mneme) transcribed by hand from a 2026-07-07 source survey (declared, not
  re-checked at runtime); external manifests via `load_dir` over `*.interop.json`.
- CLI: `discover`, `wiring`, `plan`, `route`, `validate`.
- 17 falsifiers; zero runtime dependencies.
