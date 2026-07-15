"""registry.py — the built-in manifests, transcribed from a one-time code survey.

Each capability key and module pointer below was transcribed by hand from the
flagship source during a 2026-07-07 survey. plexus does not re-read that source
at runtime, so these pointers are DECLARED citations, not probed receipts: if a
flagship renames a cited symbol, the manifest here goes stale silently until the
next manual survey. Capability keys are aligned across producers and consumers so
a declared edge forms where the code composed at survey time: gather.digest/1 ->
crucible, gather.items/1 -> mneme, mneme.crucible-export/1 (as crucible.thesis/1)
-> crucible, index.verification/1 -> crucible, and every flagship's
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
        ],
        "consumes": [
            {"capability": "crucible.thesis/1", "title": "thesis JSON",
             "module": "src/crucible/commands.py:_thesis_from_data"},
            {"capability": "crucible.measurements/1", "title": "per-claim measurements",
             "module": "src/crucible/commands.py:_load_measurements"},
            {"capability": "gather.digest/1", "title": "gather digest as evidence",
             "module": "src/crucible/ecosystem_measure.py:GatherDigestMeasure"},
            {"capability": "index.verification/1", "title": "index structural verdict",
             "module": "src/crucible/ecosystem_measure.py:verify_index_verification"},
        ],
        "evidence": ["src/crucible/ecosystem_measure.py", "src/crucible/commands.py",
                     "src/crucible/assess.py", "src/crucible/gate.py"],
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
        ],
        "consumes": [
            {"capability": "gather.items/1", "title": "accountable intake items",
             "module": "src/mneme/ingest.py:from_gather"},
            {"capability": "conversation-turns/1", "title": "raw turns to remember",
             "module": "src/mneme/memory.py:AgentMemory.remember"},
        ],
        "evidence": ["src/mneme/compose.py", "src/mneme/ingest.py",
                     "src/mneme/receipt.py", "src/mneme/drift.py"],
    },
]


def builtin_manifests() -> list:
    """The five grounded flagship manifests."""
    return [Manifest.from_dict(d) for d in _SEED]


def load_dir(path: str) -> list:
    """Load every *.interop.json manifest in a directory (external tools)."""
    out = []
    for name in sorted(os.listdir(path)):
        if name.endswith(".interop.json"):
            with open(os.path.join(path, name), encoding="utf-8") as f:
                out.append(Manifest.from_dict(json.load(f)))
    return out
