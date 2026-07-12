# plexus

**Capability discovery and auto-wiring for agent toolchains.** Point it at a set
of tools and it discovers what each one emits and consumes, then wires producer
to consumer into a runnable pipeline. Zero runtime dependencies.

MCP tells an agent *that tools exist*. plexus tells it *how their outputs plug
into each other's inputs*: the layer above a flat tool list.

```
$ plexus discover --builtin
$ plexus plan --goal crucible
$ plexus route --from gather --to crucible
```

## The problem

You wire up five tools. Each one produces artifacts and accepts inputs, but
nothing knows how they connect, so you hand-wire `A | B | C` every time and
rediscover the plumbing on every new task. plexus makes the toolchain
self-describing: each tool ships a small manifest of what it emits and consumes,
and plexus computes the wiring graph: which tool's output is which tool's input.

## What you get

**Discover the mesh.** Every producer→consumer edge, by capability:

```
$ plexus wiring --builtin
{
  "crucible.thesis/1":                [["mneme", "crucible"]],
  "gather.digest/1":                  [["gather", "crucible"]],
  "gather.items/1":                   [["gather", "mneme"]],
  "index.verification/1":             [["index", "crucible"]],
  "project-telos.flagship-action/v1": [["crucible","index"],["forum","index"],["gather","index"]]
}
```

**Plan a pipeline.** "I want to feed `crucible`. What produces its inputs?"

```
$ plexus plan --goal crucible
  order:   forum -> gather -> mneme -> crucible -> index
  sources: forum, gather
  cyclic:  crucible <-> index      # a real feedback loop, reported not hidden
```

**Route between two tools.** "I have `gather` output and want a `crucible`
verdict. How do they connect?"

```
$ plexus route --from gather --to crucible
  [gather -> crucible via gather.digest/1]
```

## How a tool plugs in

A manifest is plain JSON. A tool ships one and it joins the mesh. Drop
`*.interop.json` files in a directory and `plexus discover --dir DIR` reads them:

```json
{
  "organ": "mytool",
  "invoke": {"cli": "mytool", "mcp_server": "mytool.mcp:serve", "python_import": "mytool"},
  "emits": [
    {"capability": "mytool.report/1", "title": "analysis report",
     "module": "src/mytool/report.py:build", "consumable_as": ["crucible.thesis/1"]}
  ],
  "consumes": [
    {"capability": "gather.digest/1", "title": "evidence intake",
     "module": "src/mytool/intake.py:load"}
  ]
}
```

An edge `A -> B` forms when `B` consumes a capability that `A` emits (directly,
or via `consumable_as`, the way a producer declares "my output is also
consumable as X"). Matching is by capability string, so an edge only exists where
the tools genuinely compose.

## Grounded, not asserted

Every edge cites the **module** that produces it (`file:function`), so a claimed
connection traces back to real code. The built-in manifests for the five
flagships (gather, crucible, forum, index, mneme) were read out of their actual
source, not invented.

plexus is also honest about what does **not** connect:

- `orphans().unmet_inputs`: capabilities something consumes that nothing in the
  set emits (an external or human input).
- `orphans().unconsumed_outputs`: artifacts nobody downstream consumes (terminal
  outputs).
- `plan(...).cyclic`: feedback loops, surfaced instead of forced into a false
  linear order.

## Install

```
pip install git+https://github.com/HarperZ9/plexus.git
```

## Library

```python
from plexus import builtin_manifests, discover, plan_to, route

mesh = discover(builtin_manifests())
mesh.edges                      # every producer -> consumer edge, with evidence
mesh.wiring()                   # capability -> [(producer, consumer)]
mesh.orphans()                  # unmet inputs / unconsumed outputs
plan_to(mesh, "crucible")       # the upstream pipeline (+ any cycles)
route(mesh, "gather", "crucible")   # the capability path between two tools
```

## License

MIT. See [LICENSE](LICENSE).
