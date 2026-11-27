# Security Policy

## Supported versions

`plexus-mesh` is distributed on PyPI and provides local multi-repository discovery, dependency mesh
indexing, and a stdio MCP server. Security fixes ship in the current release line as a new release.
Older lines do not receive backports.

| Version | Supported |
|-|-|
| 0.4.x | Yes |
| < 0.4 | No |

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub: open this repository's **Security** tab
and select **Report a vulnerability**, or open
<https://github.com/HarperZ9/plexus/security/advisories/new>.
Keep security reports out of public issues, pull requests, and discussions.

Include:

- the affected version and operating system,
- a concise description of the issue and its impact,
- the minimal input or steps needed to reproduce it.

The maintainer, Zain Dana Harper, acknowledges reports and works on a fix before public disclosure.
Allow a reasonable period to remediate before disclosing.

## Scope and trust model

Plexus builds and queries local multi-repository mesh metadata and exposes structured lookup tools.

- **Local-first execution.** Core mesh indexing and queries run locally against files you specify,
  with zero telemetry and no background network listeners.
- **MCP surface.** The MCP server speaks JSON-RPC over stdio, binds no network port, and serves
  structured queries against the configured mesh state. Tool responses flow to the connected MCP
  client and its configured provider.
- **Untrusted metadata.** Repository manifests and graph inputs are treated strictly as data, never
  as executable code.
- **What counts as a vulnerability.** Code execution from untrusted mesh or manifest inputs, path
  traversal reading or writing outside configured workspace roots, or state tampering that bypasses
  integrity checks.
- **What does not count.** Malformed input files that raise a handled validation error.

## Good practice

- Restrict configured workspace roots to directories you intend to expose to MCP clients.
- Keep credentials and private keys out of indexed repository files and environment dumps.
