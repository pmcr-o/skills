# Production agent memory governance

“Agent memory” is not one bucket. This repository separates durable
instructions, personal preferences, checked lessons, workflow/session state,
checkpoints, and raw trails. Each class has a scope, owner, retention policy,
provenance, and promotion gate.

## Recommended memory layers

| Layer | Example | Default | Promotion/evidence |
|---|---|---|---|
| policy/instruction | project convention or organization rule | versioned source file | human/policy review |
| preference | user formatting choice | personal scope | explicit principal consent |
| lesson/constraint | checked PMCR-O reflection | candidate first | independent `PASS` |
| session state | current conversation/context | private, short-lived | runtime ownership |
| checkpoint | resumable MAF workflow | sensitive, encrypted | restore test and checker |
| raw trail | append-only evidence | restricted, read-only | never default context |

The active projection should be small and typed. Keep the full trail in an
evidence store and derive compact records with exact frame/checker references.
The local `pmcro-memory-governance` skill validates this contract and rejects
secret-like content, missing provenance, stale accepted lessons, and oversized
retrieval budgets.

## Scope and provider projections

Use explicit `global`, `personal`, `project`, `run`, and `session` scopes. A
personal record cannot become global merely because a project agent retrieved
it. A child surface inherits only a versioned, non-widening grant.

Provider files such as `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, or an
equivalent host directory are useful projections. Anthropic’s current Claude
Code documentation distinguishes human-authored instructions from auto memory,
describes managed/user/project scopes, and warns that these files are context
rather than enforced configuration. Keep hard controls in the runtime grant,
managed settings, hooks, tool policy, sandbox, or governance checker. See
`https://code.claude.com/docs/en/memory`.

## MAF Native mapping

Microsoft Agent Framework presents agents through a consistent interface that
combines instructions, tools, middleware, context providers, and session state.
Its workflow state is scope-aware, and checkpoints let a workflow resume from a
saved point. Map those runtime primitives to `session-state` and `checkpoint`
records, not automatically to reusable project knowledge. See
`https://learn.microsoft.com/en-us/agent-framework/concepts/agents`,
`https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/state`,
and `https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints`.

Protect serialized sessions: they may contain conversation content or session
identifiers, and restoring untrusted state can alter trust. Use access control,
encryption, bounded input/output, and rate limits. Keep sensitive telemetry off
by default; enable it only in a protected environment with a stated purpose.
See `https://learn.microsoft.com/en-us/agent-framework/concepts/agents/safety`
and `https://learn.microsoft.com/en-us/agent-framework/workflows/observability`.

## MCP and marketplace boundary

MCP tools are typed capabilities, not memory. Catalog them deterministically,
paginate large lists, bind authorization per request, validate inputs and
outputs, rate-limit calls, sanitize results, use timeouts, and log tool use for
audit. A tool may return a resource link, but the caller still resolves it
under its grant. See
`https://modelcontextprotocol.io/specification/2026-07-28/server/tools`.

For marketplace-derived memory, preserve source repository/ref, license/policy
result, skill version, disclosure level, checker verdict, freshness, and
revocation. The .NET Agent Skills repository demonstrates the useful separation
between portable skills, host-specific agents, plugins, tests, and marketplace
installation; treat its conventions as source material to pin and check, not
as authority merely because the repository exists. See
`https://github.com/dotnet/skills`.

## Release gate

Do not activate a record unless it is schema-valid, secret-free, consented,
scope-correct, provenance-linked, freshness-bounded, retrieval-budgeted, and
covered by a checker/evaluation. On source or policy drift, mark it stale and
route a bounded `LOOP`; do not silently retain stale knowledge.

This is production-readiness knowledge encoded as a checked declarative
contract. It is not a claim that this local repository has started a MAF host,
connected an MCP server, encrypted a production store, or completed a live
enterprise evaluation.

## Primary references

- Microsoft Agent Framework: agents, state, checkpoints, safety, observability,
  and evaluation: `learn.microsoft.com/en-us/agent-framework/`.
- Claude Code memory and instruction scopes: `code.claude.com/docs/en/memory`.
- MCP tools specification: `modelcontextprotocol.io/specification/2026-07-28/server/tools`.
- .NET Agent Skills repository: `github.com/dotnet/skills`.
