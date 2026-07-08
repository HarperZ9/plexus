"""Dogfood falsifier: the built-in registry must survive a round-trip through the
public *.interop.json format with the discovered mesh unchanged. If it does not,
the format cannot faithfully represent what a flagship ships — which is the whole
premise of decentralized discovery.
"""
from plexus.mesh import discover
from plexus.registry import builtin_manifests, export_all, load_dir


def _edgeset(manifests):
    return {(e.producer, e.consumer, e.capability) for e in discover(manifests).edges}


def test_builtin_manifests_roundtrip_through_json(tmp_path):
    written = export_all(str(tmp_path))
    assert len(written) == 5
    reloaded = load_dir(str(tmp_path))
    assert {m.organ for m in reloaded} == {m.organ for m in builtin_manifests()}
    # the mesh discovered from the JSON files is identical to the in-code mesh
    assert _edgeset(reloaded) == _edgeset(builtin_manifests())


def test_exported_files_are_named_per_organ(tmp_path):
    export_all(str(tmp_path))
    names = {p.name for p in tmp_path.glob("*.interop.json")}
    assert names == {"gather.interop.json", "crucible.interop.json",
                     "forum.interop.json", "index.interop.json", "mneme.interop.json"}
