"""Falsifiers for the render + run surfaces (graph export, pipeline script).

Load-bearing: (1) Mermaid/DOT export names every organ and labels every edge with
its capability, and marks self-loops distinctly; (2) the pipeline script is a
runnable, ordered invocation that ends at the target and surfaces feedback loops
as a comment rather than a false linear order.
"""
from plexus.graph import to_dot, to_mermaid
from plexus.mesh import Edge, Mesh, discover
from plexus.registry import builtin_manifests
from plexus.run import pipeline_script


def _mesh():
    return discover(builtin_manifests())


def test_mermaid_names_organs_and_labels_edges():
    m = to_mermaid(_mesh())
    assert m.startswith("flowchart LR")
    for organ in ("gather", "crucible", "mneme", "index", "forum"):
        assert f'{organ}["{organ}"]' in m
    assert '-->|"gather.digest/1"| crucible' in m          # a real cross-tool edge, labelled
    assert "-.->" in m                                     # index self-loops rendered dotted


def test_dot_is_a_digraph_with_labelled_edges():
    d = to_dot(_mesh())
    assert d.startswith("digraph plexus {") and d.rstrip().endswith("}")
    assert '"gather" -> "crucible" [label="gather.digest/1"]' in d
    assert "style=dotted" in d                             # self-loop styling present


def test_render_uses_distinct_ids_for_names_with_the_same_legacy_slug():
    """Catch a renderer that aliases ``alpha-beta`` with ``alpha_beta``."""
    mesh = Mesh(
        organs=["alpha-beta", "alpha_beta"],
        edges=[Edge("alpha-beta", "alpha_beta", "cap/1", "a.py", "b.py")],
        manifests={},
    )

    mermaid_nodes = [line for line in to_mermaid(mesh).splitlines() if "[\"" in line]
    mermaid_ids = [line.strip().split("[", 1)[0] for line in mermaid_nodes]
    dot_nodes = [
        line for line in to_dot(mesh).splitlines()
        if line.startswith('  "') and " -> " not in line
    ]
    dot_ids = [line.strip().split("\"", 2)[1] for line in dot_nodes]

    assert len(mermaid_ids) == len(set(mermaid_ids)) == 2
    assert len(dot_ids) == len(set(dot_ids)) == 2


def test_render_escapes_hostile_names_and_capabilities_without_new_statements():
    """Catch a raw quote, slash, or control character escaping a graph label."""
    hostile = 'alpha\"]\\\r\nINJECTED --> target\x00\x1f\x7f'
    peer = "beta"
    capability = 'cap\"|INJECTED --> target|\\\r\n\x00\x1f\x7f'
    mesh = Mesh(
        organs=[hostile, peer],
        edges=[Edge(hostile, peer, capability, "a.py", "b.py")],
        manifests={},
    )

    mermaid = to_mermaid(mesh)
    dot = to_dot(mesh)

    # Only the renderer's own statements may occupy physical output lines.
    assert len(mermaid.splitlines()) == 4
    assert len(dot.splitlines()) == 7
    for rendered in (mermaid, dot):
        assert '\\"' in rendered and "\\\\" in rendered
        assert "\\r" in rendered and "\\n" in rendered
        assert "\\x00" in rendered and "\\x1f" in rendered and "\\x7f" in rendered
        assert '"INJECTED --> target' not in rendered


def test_current_slug_shaped_registry_output_keeps_its_existing_identifiers():
    mermaid = to_mermaid(_mesh())
    dot = to_dot(_mesh())

    assert 'flywheel_infra["flywheel-infra"]' in mermaid
    assert '"flywheel-infra" -> "crucible"' not in dot
    assert '"learn" -> "flywheel-infra" [label="learn.tutor-misconceptions/1"]' in dot


def test_pipeline_script_is_runnable_ordered_and_ends_at_target():
    s = pipeline_script(_mesh(), "crucible")
    assert s.startswith("#!/usr/bin/env bash")
    assert "# plexus pipeline to feed: crucible" in s
    lines = [ln for ln in s.splitlines() if ln and not ln.startswith("#")]
    assert lines[-1].strip() == "crucible run"            # target invoked last
    assert "gather run" in s                              # an upstream source is invoked


def test_pipeline_script_surfaces_the_feedback_loop():
    s = pipeline_script(_mesh(), "crucible")
    assert "feedback loop" in s and "crucible <-> index" in s


def test_pipeline_script_reports_unknown_target():
    assert "error" in pipeline_script(_mesh(), "nope")
