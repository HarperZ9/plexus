"""Grounding falsifiers: the built-in registry must produce the REAL flagship
edges (the ones the code already composes), not invented ones. If a flagship's
interop surface changes and the manifest goes stale, these break.
"""
from plexus.mesh import discover
from plexus.plan import plan_to, route
from plexus.registry import builtin_manifests


def _mesh():
    return discover(builtin_manifests())


def _edge(mesh, producer, consumer, capability):
    return any(e.producer == producer and e.consumer == consumer
               and e.capability == capability for e in mesh.edges)


def test_the_five_flagships_are_present():
    assert set(_mesh().organs) == {"gather", "crucible", "forum", "index", "mneme"}


def test_real_cross_flagship_edges_form():
    m = _mesh()
    assert _edge(m, "gather", "crucible", "gather.digest/1")          # ecosystem_measure
    assert _edge(m, "gather", "mneme", "gather.items/1")              # mneme.ingest.from_gather
    assert _edge(m, "mneme", "crucible", "crucible.thesis/1")         # compose.to_crucible_thesis
    assert _edge(m, "index", "crucible", "index.verification/1")      # verify_index_verification


def test_flagship_action_envelopes_feed_the_index_spine():
    m = _mesh()
    cap = "project-telos.flagship-action/v1"
    feeders = {e.producer for e in m.edges if e.consumer == "index" and e.capability == cap}
    assert {"gather", "crucible", "forum", "index"} <= feeders          # all peers + self

def test_every_edge_cites_a_producing_module():
    for e in _mesh().edges:
        assert e.producer_module and ":" in e.producer_module          # evidence, not assertion


def test_plan_to_crucible_pulls_the_upstream_producers():
    plan = plan_to(_mesh(), "crucible")
    assert {"gather", "mneme", "index"} <= set(plan["order"])
    assert "gather" in plan["sources"]                       # gather is a pure source


def test_the_crucible_index_feedback_loop_is_reported_not_hidden():
    # crucible's status envelope feeds index's spine; index's verification feeds
    # crucible's measurement -> a real 2-cycle the planner must surface honestly
    plan = plan_to(_mesh(), "crucible")
    assert set(plan["cyclic"]) == {"crucible", "index"}


def test_route_gather_to_crucible_is_connected():
    r = route(_mesh(), "gather", "crucible")
    assert r["connected"] and r["hops"] >= 1


def test_orphans_are_honest_about_external_inputs():
    orph = _mesh().orphans()
    # inputs that come from outside the five (human/other systems) are surfaced
    assert "external-agent-trace/1" in orph["unmet_inputs"]       # forum ingests external traces
    assert "conversation-turns/1" in orph["unmet_inputs"]         # mneme ingests raw turns
