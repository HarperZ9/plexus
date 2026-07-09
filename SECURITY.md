# Security Policy

## Supported versions

`plexus-mesh` is released from this repository. Security fixes are applied to the
current release line and published as a new patch release. Older lines are not
backported.

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a vulnerability

Please report suspected vulnerabilities privately. Do not open a public issue,
pull request, or discussion for a security report.

Send the report to `<SECURITY CONTACT>`. Include:

- the affected version and platform,
- a description of the issue and its impact,
- the minimal steps or input needed to reproduce it.

You can expect an acknowledgement, and we will work a fix before any public
disclosure. Please allow a reasonable period to remediate before disclosing.

## Scope and trust model

`plexus-mesh` discovers capabilities and auto-wires agent toolchains. It reads
local JSON interop manifests, derives a producer-to-consumer mesh, and can emit
runnable pipeline scripts. The core is zero-dependency.

- Local only: plexus reads manifests from the local filesystem and performs no
  network calls of its own. It stores no credentials.
- Untrusted manifests: a manifest is data that shapes the derived mesh and any
  generated pipeline script. Treat manifests from outside sources as untrusted,
  validate them (`plexus validate`), and review a generated pipeline script
  before you run it, since it is code assembled from manifest contents.
- MCP surface: plexus ships a stdio MCP server. It speaks JSON-RPC over stdio and
  does not open a network port on its own.

## Good practice

- Review generated pipeline scripts before execution, and run them as an
  unprivileged user.
- Keep manifests you author under version control so mesh changes are auditable.
