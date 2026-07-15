"""Cycle-9 credo falsifiers: honesty repairs to the wiring surface.

These pin the fixes for the "grounded, not asserted" overclaim and its
neighbours: an edge is a DECLARED claim (plexus probes nothing), a duplicate
organ id is NAMED not silently collapsed, the discover output carries a
re-runnable receipt, validate() FAILS on empty-module evidence and never raises
on malformed input, and plan_to reports an honest null instead of fabricating a
command for a tool that declared no CLI.
"""
from pathlib import Path

from plexus.manifest import Manifest, Port, validate
from plexus.mesh import discover
from plexus.plan import plan_to

_ROOT = Path(__file__).resolve().parents[1]


def _m(organ, emits=(), consumes=(), invoke=None):
    return Manifest(organ=organ,
                    invoke=invoke if invoke is not None else {"cli": organ},
                    emits=[e if isinstance(e, Port) else Port(*e) for e in emits],
                    consumes=[c if isinstance(c, Port) else Port(*c) for c in consumes])


# ---------------------------------------------------------------- DEFECT A
# An edge is self-declared: no probe resolves the cited module or runs the tool.
# The surface must tag it "declared", never emit verification vocabulary.

def test_every_edge_is_tagged_declared():
    a = _m("a", emits=[Port("x/1", module="a.py:x")])
    b = _m("b", consumes=[Port("x/1", module="b.py:in")])
    mesh = discover([a, b])
    assert mesh.edges
    for e in mesh.edges:
        assert e.evidence == "declared"          # plexus probed nothing


def test_readme_does_not_use_verification_vocabulary_for_declared_edges():
    text = (_ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "declared, not probed" in text        # the honest heading
    assert "grounded, not asserted" not in text
    assert "traces back to real code" not in text
    assert "genuinely compose" not in text


# ---------------------------------------------------------------- DEFECT B
# A duplicate organ id must be NAMED, not silently resolved last-writer-wins
# (the roster keeps the winner while edges are minted from both).

def test_duplicate_organ_id_is_surfaced_as_a_collision():
    real = _m("crucible", consumes=[Port("x/1", module="real.py:in")])
    impostor = _m("crucible", emits=[Port("y/1", module="evil.py:out")])
    mesh = discover([real, impostor])
    assert "crucible" in mesh.collisions       # the clash is reported, not hidden


def test_no_collision_field_stays_empty_for_a_clean_set():
    a = _m("a", emits=[Port("x/1", module="a.py:x")])
    b = _m("b", consumes=[Port("x/1", module="b.py:in")])
    assert discover([a, b]).collisions == []


def test_validate_set_flags_duplicate_organ_ids():
    from plexus.manifest import duplicate_organs
    assert duplicate_organs([_m("dup"), _m("dup"), _m("solo")]) == ["dup"]
    assert duplicate_organs([_m("a"), _m("b")]) == []


def test_validate_cli_fails_on_organ_collision(tmp_path, capsys):
    import json as _json

    from plexus.cli import main
    (tmp_path / "a.interop.json").write_text(_json.dumps(
        {"organ": "gather", "emits": [{"capability": "x/1", "module": "a.py:x"}]}))
    (tmp_path / "b.interop.json").write_text(_json.dumps(
        {"organ": "gather", "invoke": {"cli": "evil"}}))
    rc = main(["validate", "--dir", str(tmp_path)])
    out = _json.loads(capsys.readouterr().out)
    assert rc == 1                               # collision cannot launder to ok
    assert out["duplicate_organs"] == ["gather"]


# ---------------------------------------------------------------- DEFECT C
# The primary output must carry a re-runnable receipt: per-manifest source +
# content hash, plus the plexus version (tenet 3, no receipt no accept).

def test_content_hash_is_stable_and_binds_content():
    from plexus.manifest import content_hash
    a = _m("t", emits=[Port("x/1", module="a.py:x")])
    b = _m("t", emits=[Port("x/1", module="a.py:x")])
    c = _m("t", emits=[Port("x/1", module="a.py:CHANGED")])
    assert content_hash(a) == content_hash(b)    # same content, same hash
    assert content_hash(a) != content_hash(c)    # a changed pointer changes it
    assert len(content_hash(a)) == 64            # sha256 hex


def test_load_dir_tags_manifest_source(tmp_path):
    import json as _json

    from plexus.registry import builtin_manifests, load_dir
    (tmp_path / "mytool.interop.json").write_text(_json.dumps(
        {"organ": "mytool", "emits": [{"capability": "x/1", "module": "a.py:b"}]}))
    loaded = load_dir(str(tmp_path))
    assert loaded[0].source.endswith("mytool.interop.json")
    assert all(m.source == "builtin:registry" for m in builtin_manifests())


def test_discover_output_carries_a_receipt():
    from plexus.cli import _mesh_json
    from plexus.registry import builtin_manifests
    j = _mesh_json(discover(builtin_manifests()))
    rec = j["receipt"]
    assert rec["plexus_version"]
    assert "generated_utc" in rec
    entries = {e["organ"]: e for e in rec["manifests"]}
    assert entries["gather"]["source"] == "builtin:registry"
    assert all(len(e["sha256"]) == 64 for e in rec["manifests"])
