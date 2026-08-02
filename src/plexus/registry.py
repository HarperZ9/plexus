"""registry.py — the built-in manifests, transcribed from a one-time code survey.

Each capability key and module pointer below was transcribed by hand from the
flagship source during a 2026-07-07 survey. plexus does not re-read that source
at runtime, so these pointers are DECLARED citations, not probed receipts: if a
flagship renames a cited symbol, the manifest here goes stale silently until the
next manual survey. Capability keys are aligned across producers and consumers so
a declared edge forms where the code composed at survey time: gather.digest/1 ->
crucible, gather.items/1 -> mneme, mneme.crucible-export/1 (as crucible.thesis/1)
-> crucible, crucible.replay-template/1 -> mneme,
crucible.replay-pack/1 -> crucible, index.verification/1 -> crucible, and every flagship's
project-telos.flagship-action/v1 envelope -> index's spine loader.

External manifests can be loaded from a directory of *.interop.json files with
the same shape (see Manifest.to_dict), so a tool ships its own contract.
"""
from __future__ import annotations

import json
import os

from .manifest import Manifest

FLAGSHIP = "project-telos.flagship-action/v1"

_SEED = [
    {
        "organ": "gather",
        "invoke": {"cli": "gather", "mcp_server": "gather.mcp:serve", "python_import": "gather"},
        "emits": [
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/gather/flagship.py:envelope"},
            {"capability": "gather.digest/1", "title": "witnessed digest seal",
             "module": "src/gather/digest.py:Digest.to_json"},
            {"capability": "gather.items/1", "title": "per-item provenance receipts",
             "module": "src/gather/digest.py:_receipt"},
            {"capability": "gather.catalog-digest/1", "title": "docs/arxiv catalog + digest",
             "module": "src/gather/payloads.py:catalog_digest_payload"},
        ],
        "consumes": [
            {"capability": "provenance.verdict/1", "title": "external provenance verdict",
             "module": "src/gather/provenance.py:SubprocessProvenanceProvider.origin"},
            {"capability": "gather.run-config/1", "title": "multi-source run config",
             "module": "src/gather/run_config.py:load_run_config"},
        ],
        "evidence": ["src/gather/interop.py", "src/gather/digest.py",
                     "src/gather/payloads.py", "src/gather/flagship.py"],
    },
    {
        "organ": "crucible",
        "invoke": {"cli": "crucible", "mcp_server": "crucible.mcp:serve", "python_import": "crucible"},
        "emits": [
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/crucible/flagship.py:envelope"},
            {"capability": "crucible.assessment/1", "title": "witnessed assessment",
             "module": "src/crucible/assess.py:Assessment.to_dict"},
            {"capability": "project-telos.crucible.measurement-gate/v1", "title": "measurement gate",
             "module": "src/crucible/measurement_gate.py:_result"},
            {"capability": "crucible.thesis-export/1", "title": "public thesis contract",
             "module": "src/crucible/gate.py:export_thesis"},
            {"capability": "crucible.replay-template/1", "title": "oracle replay template",
             "module": "src/crucible/recheck_cmd.py:_write_template"},
        ],
        "consumes": [
            {"capability": "crucible.thesis/1", "title": "thesis JSON",
             "module": "src/crucible/commands.py:_thesis_from_data"},
            {"capability": "crucible.measurements/1", "title": "per-claim measurements",
             "module": "src/crucible/commands.py:_load_measurements"},
            {"capability": "crucible.replay-pack/1", "title": "assessment-bound replay pack",
             "module": "src/crucible/recheck_cmd.py:_load_replay_pack"},
            {"capability": "gather.digest/1", "title": "gather digest as evidence",
             "module": "src/crucible/ecosystem_measure.py:GatherDigestMeasure"},
            {"capability": "index.verification/1", "title": "index structural verdict",
             "module": "src/crucible/ecosystem_measure.py:verify_index_verification"},
        ],
        "evidence": ["src/crucible/ecosystem_measure.py", "src/crucible/commands.py",
                     "src/crucible/assess.py", "src/crucible/gate.py",
                     "src/crucible/recheck_cmd.py"],
    },
    {
        "organ": "forum",
        "invoke": {"cli": "forum", "mcp_server": "forum.mcp_surface:serve_stdio", "python_import": "forum"},
        "emits": [
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/forum/flagship.py:envelope"},
            {"capability": "forum.flight-recorder/1", "title": "trace -> verifiable ledger",
             "module": "src/forum/flight_recorder.py:import_trace"},
            {"capability": "project-telos.action-receipt/v1", "title": "submit action receipt",
             "module": "src/forum/receipts.py:submit_receipt"},
            {"capability": "forum.context-capsule/v1", "title": "witnessed context capsule",
             "module": "src/forum/context_capsule.py:build_context_capsule"},
        ],
        "consumes": [
            {"capability": "external-agent-trace/1", "title": "LangSmith/OTel/AgentOps trace",
             "module": "src/forum/flight_recorder.py:normalize_trace"},
        ],
        "evidence": ["src/forum/ledger.py", "src/forum/flight_recorder.py",
                     "src/forum/flagship.py", "src/forum/receipts.py"],
    },
    {
        "organ": "index",
        "invoke": {"cli": "index", "mcp_server": "index_graph.mcp:serve", "python_import": "index_graph"},
        "emits": [
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/index_graph/flagship.py:envelope"},
            {"capability": "project-telos.context-envelope/v1", "title": "budgeted context envelope",
             "module": "src/index_graph/context/envelope.py:build_context_envelope"},
            {"capability": "index.verification/1", "title": "structural-claim verdict",
             "module": "src/index_graph/verify.py:build_verification"},
            {"capability": "index.invalidation-pin/1", "title": "freshness pin",
             "module": "src/index_graph/freshness/invalidate.py:mint_pin"},
            {"capability": "index.wiki/1", "title": "sealed commit-pinned wiki",
             "module": "src/index_graph/wiki/pack.py:build_wiki_pack"},
        ],
        "consumes": [
            {"capability": FLAGSHIP, "title": "peer envelopes into the operator spine",
             "module": "src/index_graph/workbench.py:load_spine"},
            {"capability": "index.invalidation-pin/1", "title": "pin to diff against the tree",
             "module": "src/index_graph/freshness/invalidate.py:invalidation_report"},
            {"capability": "index.wiki/1", "title": "sealed wiki to re-verify",
             "module": "src/index_graph/wiki/seal.py:verify_wiki"},
        ],
        "evidence": ["src/index_graph/flagship.py", "src/index_graph/context/envelope.py",
                     "src/index_graph/verify.py", "src/index_graph/workbench.py"],
    },
    {
        "organ": "mneme",
        "invoke": {"cli": "mneme", "mcp_server": "mneme.mcp:serve", "python_import": "mneme"},
        "emits": [
            {"capability": "mneme.crucible-export/1", "title": "memory as crucible thesis",
             "module": "src/mneme/compose.py:to_crucible_thesis",
             "consumable_as": ["crucible.thesis/1"]},
            {"capability": "mneme.provenance-chain/1", "title": "memory -> source origin",
             "module": "src/mneme/ingest.py:provenance_chain"},
            {"capability": "mneme.recall/1", "title": "re-derivable recall receipt",
             "module": "src/mneme/receipt.py:RecallReceipt.as_dict"},
            {"capability": "mneme.drift-report/1", "title": "memory faithfulness verdicts",
             "module": "src/mneme/drift.py:drift_report"},
            {"capability": "crucible.replay-pack/1", "title": "assessment-bound replay pack",
             "module": "src/mneme/replay.py:replay_crucible"},
        ],
        "consumes": [
            {"capability": "gather.items/1", "title": "accountable intake items",
             "module": "src/mneme/ingest.py:from_gather"},
            {"capability": "conversation-turns/1", "title": "raw turns to remember",
             "module": "src/mneme/memory.py:AgentMemory.remember"},
            {"capability": "crucible.replay-template/1", "title": "oracle replay template",
             "module": "src/mneme/replay.py:replay_crucible"},
        ],
        "evidence": ["src/mneme/compose.py", "src/mneme/ingest.py",
                     "src/mneme/receipt.py", "src/mneme/drift.py",
                     "src/mneme/replay.py"],
    },
    {
        "organ": "learn",
        "invoke": {"cli": "learn", "mcp_server": "src/mcp.mjs", "node_entry": "src/mcp.mjs"},
        "emits": [
            {"capability": "learn-receipt", "title": "tutor credential/mastery ledger entries",
             "module": "src/interop.mjs:receiptEntry"},
            {"capability": "learn.tutor-mastery/1", "title": "mastery gate verdict",
             "module": "src/tutor/tutor.mjs:mastery"},
            {"capability": "learn.tutor-prooflesson/1", "title": "proof packet to lesson scaffold",
             "module": "src/tutor/prooflesson.mjs:proofLesson"},
            {"capability": "learn.tutor-misconceptions/1", "title": "ranked misconception aggregation",
             "module": "src/tutor/misconception.mjs:misconceptions"},
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/interop.mjs:receiptEntry"},
        ],
        "consumes": [
            {"capability": "crucible.thesis/1", "title": "crucible thesis for proof lesson",
             "module": "src/tutor/prooflesson.mjs:proofLesson"},
        ],
        "evidence": ["src/interop.mjs", "src/tutor/tutor.mjs",
                     "src/tutor/prooflesson.mjs", "src/tutor/misconception.mjs"],
    },
    {
        "organ": "telos",
        "invoke": {"cli": "telos", "mcp_server": "demo/telos-mcp.mjs", "node_entry": "demo/telos-mcp.mjs"},
        "emits": [
            {"capability": "telos.room/1", "title": "five-flagship room summary",
             "module": "src/telos-mcp.mjs:telos_room"},
            {"capability": "telos.workflow/1", "title": "golden workflow verification",
             "module": "src/telos-mcp.mjs:telos_workflow"},
            {"capability": "telos.status/1", "title": "workbench readiness + next actions",
             "module": "src/telos-mcp.mjs:telos_status"},
            {"capability": FLAGSHIP, "title": "flagship-action envelope",
             "module": "src/telos-mcp.mjs:telos_status"},
        ],
        "consumes": [
            {"capability": "project-telos.flagship-action/v1", "title": "cross-tool action",
             "module": "src/telos-mcp.mjs:telos_room"},
        ],
        "evidence": ["demo/telos-mcp.mjs"],
    },
    {
        "organ": "flywheel-infra",
        "invoke": {"cli": "flywheel", "python_import": "harness"},
        "emits": [
            {"capability": "flywheel.egress/1", "title": "sealed egress event receipt",
             "module": "harness/infra/egress.py:build_egress_receipt"},
            {"capability": "flywheel.lesson/1", "title": "sealed organizational lesson",
             "module": "harness/lesson.py:build_lesson"},
            {"capability": "flywheel.tool-call-receipt/1", "title": "sealed tool-call receipt",
             "module": "harness/tool_call_receipt.py:build_receipt"},
            {"capability": "flywheel.tadr-classification/1", "title": "sealed tier classification",
             "module": "harness/governance/tadr_receipt.py:build_classification_receipt"},
            {"capability": "flywheel.governance-envelope/1", "title": "cross-lane governance state",
             "module": "harness/governance_envelope.py:GovernanceEnvelope"},
            {"capability": "flywheel.credential-scan/1", "title": "sealed credential exposure report",
             "module": "harness/infra/credential_scanner.py:build_credential_scan_receipt"},
            {"capability": "flywheel.correlated-event/1", "title": "cross-layer correlated detection",
             "module": "harness/infra/correlator.py:build_correlated_receipt"},
            {"capability": "flywheel.isolation-test/1", "title": "boundary test verdict",
             "module": "harness/infra/isolation_test.py:run_isolation_test"},
            {"capability": "flywheel.kill-switch/1", "title": "dual-confirmed infrastructure stop",
             "module": "harness/infra/kill_switch.py:build_kill_receipt"},
            {"capability": "flywheel.run-bom/1", "title": "sealed run bill of materials",
             "module": "harness/infra/run_bom.py:RunBOM.sealed"},
        ],
        "consumes": [
            {"capability": "accountable-surface.actuation-outcome/1",
             "title": "intent-vs-outcome for lesson derivation",
             "module": "harness/lesson_mappers.py:intent_outcome_lessons"},
            {"capability": "mneme.drift-report/1",
             "title": "memory drift for lesson derivation",
             "module": "harness/lesson_mappers.py:drift_lessons"},
            {"capability": "learn.tutor-misconceptions/1",
             "title": "graded failures for lesson derivation",
             "module": "harness/lesson_mappers.py:misconception_lessons"},
        ],
        "evidence": ["harness/lesson.py", "harness/infra/egress.py",
                     "harness/governance/tadr_receipt.py",
                     "harness/tool_call_receipt.py"],
    },
]


def builtin_manifests() -> list:
    """The built-in flagship manifests, tagged with their in-code source.

    Covers: gather, crucible, index, forum, mneme, learn, telos, flywheel-infra.
    """
    out = []
    for d in _SEED:
        m = Manifest.from_dict(d)
        m.source = "builtin:registry"
        out.append(m)
    return out


def probe_lane(name: str, timeout: float = 10.0) -> dict:
    """Probe a lane by spawning its MCP server and calling status/doctor.

    Unlike the declared manifest (which cites source files without running
    them), this actually spawns the lane and verifies it responds. Returns
    {name, reachable, tools, error}.

    Requires the lane's MCP server to be installed and on PATH.
    """
    result = {"name": name, "reachable": False, "tools": [], "error": ""}
    try:
        from harness.lanes import resolve_mcp_command, LANES
        if name not in LANES:
            result["error"] = f"unknown lane: {name}"
            return result
        command = resolve_mcp_command(name)
    except ImportError:
        result["error"] = "harness.lanes not available (run from flywheel)"
        return result
    except Exception as e:
        result["error"] = f"resolve failed: {e}"
        return result

    try:
        with MCPClient(command, timeout=timeout,
                       client_name=f"plexus-probe-{name}") as c:
            c.start()
            tools_res = c.call_text("tools/list", {})
            if tools_res["ok"]:
                import json as _json
                try:
                    data = _json.loads(tools_res["text"])
                    if isinstance(data, list):
                        result["tools"] = data
                    elif isinstance(data, dict) and "tools" in data:
                        result["tools"] = data["tools"]
                except _json.JSONDecodeError:
                    pass
            status_res = c.call_text("status", {})
            result["reachable"] = status_res["ok"]
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def probe_all(timeout: float = 10.0) -> list[dict]:
    """Probe all built-in lanes. Returns a list of probe results."""
    try:
        from harness.lanes import LANES
        names = sorted(LANES.keys())
    except ImportError:
        names = [m.organ for m in builtin_manifests()]
    return [probe_lane(name, timeout=timeout) for name in names]


def load_dir(path: str) -> list:
    """Load every *.interop.json manifest in a directory (external tools). Each
    manifest records the file it was read from as its provenance source."""
    out = []
    for name in sorted(os.listdir(path)):
        if name.endswith(".interop.json"):
            full = os.path.join(path, name)
            with open(full, encoding="utf-8") as f:
                m = Manifest.from_dict(json.load(f))
            m.source = full
            out.append(m)
    return out


def export_all(out_dir: str) -> list:
    """Write each built-in manifest as <organ>.interop.json — the exact file a
    flagship would ship to join the mesh. Returns the paths written."""
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for m in builtin_manifests():
        p = os.path.join(out_dir, f"{m.organ}.interop.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(m.to_dict(), f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(p)
    return written
