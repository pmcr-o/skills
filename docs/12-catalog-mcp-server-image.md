# Pre-build charter: trail-derived catalog MCP server image

This is a design boundary for a future container image. It is not the image, an MCP runtime, or a claim that the current repository has connected to another session.

## Intent

Build a read-only catalog MCP server whose entries are derived from checked PMCR-O skill trails. A trail can simulate a capability, expose a domain-specific `I AM` role surface, and produce a candidate specialization. It becomes a catalog entry only after provenance, scope, limits, and an independent checker verdict are present.

The server should make the trail progressively useful:

```text
checked trail -> candidate capability -> domain specialization -> checked catalog entry -> requestable package
```

Simulation is evidence for design, not runtime evidence. A simulated `I AM` voice is a bounded lens; it is not a person, credential, authority grant, or proof that an MCP server exists.

## Two-session boundary

The current session and another session are separate entrypoints. They do not share hidden memory or a common maker/checker identity.

| Entrypoint | Responsibility | May hand off |
| --- | --- | --- |
| `entrypoint:thought-transfer-pmcro` | preserve seed, package trails, project candidate skills, and prepare the activation bundle | versioned package, trail event IDs, checker verdict, source commit |
| `entrypoint:catalog-mcp-build` | plan and build the server/image from an approved catalog contract | staged image digest, tool schema, read-only test evidence |

The handoff between them is an explicit PMCR-O envelope containing `runId`, `parentRunId`, `principal`, `domainId`, `charterId`, `scope`, `allowedTools`, finite limits, source trail IDs, and checker evidence. The receiving session must not treat a package as permission to widen scope.

## Catalog entry contract

Each promoted entry should carry at least:

- stable `skillId` and semantic version;
- domain and supported entrypoints/accounts;
- input and output envelope types;
- source trail event IDs and Git source commit;
- simulation status and redaction/provenance metadata;
- capability grants, refusal conditions, finite limits, and side-effect class;
- independent checker verdict and acceptance evidence; and
- package IDs needed for progressive disclosure.

Suggested lifecycle:

```text
candidate -> checked -> staged -> promoted
             |          |
             +-> loop   +-> halt
```

Only the orchestrator may consume the next seed. The catalog server is a read-only projection by default; it cannot self-promote an entry, mint authority, execute arbitrary tools, or turn a new session into a child without an explicit charter.

## MCP surface to design later

The initial server can expose only typed, read-only operations:

1. `catalog.search` — find entries by domain, skill ID, flow, or package ID;
2. `catalog.get` — return one entry plus provenance and checker evidence;
3. `catalog.request_package` — return the smallest next package named by the core contract; and
4. `catalog.simulation` — return a clearly labeled simulation frame, never runtime proof.

An image build may add a separate write path later, but it must not be bundled into the first read-only image. No credentials, account tokens, raw backup codes, or unredacted private transcripts belong in the image or catalog.

## PMCR-O pre-build graph

```text
orchestrator -> trail projector -> catalog schema maker -> independent checker -> reflector
```

Acceptance before an image build starts:

- the catalog schema is versioned and maps every entry to checked trail IDs;
- the two-session handoff is explicit and scope-preserving;
- simulation, candidate, checked, and promoted states are distinct;
- the server surface is read-only and package-aware;
- a fresh checker can reject an entry without changing the maker artifact; and
- the image build has a finite tool/turn/depth/output limit and a reproducible source commit.

The next seed is to plan the catalog schema and dry-run tool envelopes. It does not authorize Docker, MCP publication, account access, or an image build yet.
