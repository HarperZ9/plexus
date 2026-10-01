## Marketplace source distribution

This folder packages the source plugin from release 0.3.0. It requires Python 3.11 or later, available as `python3`. It includes the tool source and no model or bundled runtime. The connected client supplies any model used in the conversation.

The separate [Windows x64 native download](https://github.com/HarperZ9/plexus/releases/download/v0.3.0/plexus-0.3.0-win-x64.mcpb) includes its runtime. That download is a manual MCPB package and is not part of this source plugin. Directory approval and availability remain unverified.

This branch contains the installable plugin. Build commands in the release README below apply to the [product source tag](https://github.com/HarperZ9/plexus/tree/v0.3.0). DISTRIBUTION.json records the published asset digest and every packaging change; any SOURCE.json describes the original release payload.

# Plexus client package

Discovery, wiring, plans and routes describe manifests. A declared edge does not prove installation, execution, compatibility or successful data transfer. Optional directory arguments read caller-selected manifest files. This adapter never invokes pipeline scripts or probe helpers.

## Install
The source ZIP requires Python 3.11 or newer. Extract the entire archive, then point a local stdio MCP client at an absolute Python executable with arguments `-I -S -B server/serve.py` using the absolute script path. Plexus needs no required environment binding. The source package is an advanced installation, not self-contained.

The Windows x64 native ZIP includes Python and needs no separate Python or Node installation. Extract everything and use the absolute `server/plexus-local.exe` path with no arguments. A client supporting binary MCPB extensions may open the matching MCPB. Both archives use identical executable bytes.

Portable plugin.json/mcp.json, Claude's .claude-plugin/plugin.json and .mcp.json, and Codex's .codex-plugin/plugin.json are generated from the same source version. The source manifests use python3; replace that command with an absolute trusted Python path if unavailable. No client configuration is modified automatically. ChatGPT or Claude cloud support and marketplace admission are not implied by local MCP compatibility.

## Troubleshooting
An unknown launch argument stops startup. Restart the client after correcting its command. Optional directory arguments select local manifest files; review those paths before each call. Check SHA256SUMS before extracting and keep the full package together. Unsigned Windows binaries can trigger platform warnings; Code signing and clean-machine acceptance are not established by this source distribution.

The tool source matches the published source-plugin asset; DISTRIBUTION.json records the packaging changes in this branch. No background service, network listener, cloud account or publisher compute is created.
