# Agent-surface contract

An agent surface is a typed projection, not a claim that every component is an
LLM agent. It gives the orchestrator one envelope for an agent, service, tool,
workflow, resource, plugin, or MCP endpoint.

Required identity fields:

- `apiVersion`, `kind`, `id`, `version`, `scope`, `owner`, and `templateRef`.
- `independentSurface: true` means this capability has its own addressable
  contract. It does not mean the capability is an independent checker.
- `extends` is either `null` or a versioned parent with `policy: non-widening`.
- `role` and `capabilityType` distinguish an orchestrator from a service or
  tool; identity labels do not create authority.

Required behavior fields:

- `entrypoints`, `inputs`, `outputs`, `dependencies`, `modes`, `grant`, and
  `limits`.
- `accept` and `deny` are typed contract outcomes. Missing authority fails
  closed; a model response cannot grant a filesystem or network capability.
- `independentChecker: true` is reserved for a fresh, verdict-only checker;
  ordinary planners, makers, catalogs, and reflectors keep it false.
- `status` carries `mode`, `simulation`, `verified`, `evidenceTier`,
  `checkerRef`, and `trailRef`.

The recommended scope projection is:

| Scope | Owns | Must not imply |
|---|---|---|
| `global` | shared templates, catalog policy, public defaults | private memory or project writes |
| `personal` | one principal's preferences and grants | changes to global defaults |
| `project` | repository layout, project agents, local workflows | account-wide authority |
| `run` | one cycle's ephemeral state and evidence | persistent promotion |

The mode contract is identical across modes. Only the runtime adapter changes.
`inspect` reads metadata, `simulate` predicts with side effects disabled,
`replay` consumes a checked trace, `execute` invokes a verified entrypoint, and
`check` independently evaluates the result.
