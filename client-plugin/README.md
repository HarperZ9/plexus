# Plexus client package

Plexus reads the manifests your local tools publish and shows which tool produces each capability, which tool consumes it, and the path between any two tools.

## Try it

- Show which tools produce and consume each capability.
- Plan the pipeline that feeds Crucible.
- Find the shortest route from Gather to Crucible.

## Details

Discovery, wiring, plans and routes describe manifests. A declared edge does not prove installation, execution, compatibility or successful data transfer. Optional directory arguments read caller-selected manifest files. This adapter never invokes pipeline scripts or probe helpers.

## Install
The source ZIP requires Python 3.11 or newer. Extract the entire archive, then point a local stdio MCP client at an absolute Python executable with arguments `-I -S -B server/serve.py` using the absolute script path. Plexus takes no path, account or grant at launch. The source package is an advanced installation, not self-contained.

In Claude Code, enabling the plugin asks for nothing. Plexus needs no settings, so the Claude manifest declares no `userConfig` and launches `python3 -I -S -B ${CLAUDE_PLUGIN_ROOT}/server/serve.py` with no further arguments. Replace `python3` with a trusted absolute Python path where necessary.

The Windows x64 native ZIP includes Python and needs no separate Python or Node installation. Extract everything and use the absolute `server/plexus-local.exe` path with no arguments. A client supporting binary MCPB extensions may open the matching MCPB, which has no settings to enter. Both archives use identical executable bytes.

Portable plugin.json/mcp.json, Claude's .claude-plugin/plugin.json and .mcp.json, and Codex's .codex-plugin/plugin.json are generated from the same source version. The source manifests use python3; replace that command with an absolute trusted Python path if unavailable. No client configuration is modified automatically. ChatGPT or Claude cloud support and marketplace admission are not implied by local MCP compatibility.

## Data and network

| Question | Answer |
| --- | --- |
| What it reads | The tool manifests built into Plexus and, when a call names a folder, the `*.interop.json` files in that folder |
| What it stores | Nothing. Every call computes its answer in memory and writes no file |
| Network calls | None. The server opens no socket and starts no other program |
| Telemetry | None |
| Retention | Nothing is kept after a call returns |

Call results go to the connected client, and that client's model provider handles them under its own privacy policy. See [PRIVACY.md](PRIVACY.md).

## Troubleshooting
An unknown launch argument stops startup. Remove it and restart the client. A folder argument that is missing or holds a malformed manifest returns a tool error, and the server keeps running. Check SHA256SUMS before extracting and keep the full package together. Unsigned Windows binaries can trigger platform warnings; signing and clean-machine/client acceptance remain release gates.

These development bytes may carry the current source version but are not the existing published release. No background service, network listener, cloud account or publisher compute is created.
