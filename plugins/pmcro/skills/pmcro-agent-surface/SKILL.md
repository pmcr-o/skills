---
name: pmcro-agent-surface
description: Expose a component, service, plugin, workflow, MCP endpoint, or marketplace skill as a typed PMCR-O agent surface for inspect, simulate, replay, execute, and independent check. Use for Everything-as-Agent designs such as ProjectName.OrchestrationService; dry runs never prove runtime correctness.
---

# PMCR-O agent surface

Use this skill to give a capability one stable, typed boundary. The capability
may be a MAF Native agent, .NET service, MCP endpoint, workflow, plugin, or
marketplace skill. The surface declares identity, scope, dependencies,
schemas, lifecycle, grant, limits, and evidence.

## Procedure

1. Read the smallest applicable catalog disclosure and identify the component,
   exact version/ref, entrypoint, dependencies, input/output schemas, side
   effects, and independent checker.
2. Render one activation envelope from `references/agent-surface-contract.md`.
   A scope (`global`, `personal`, `project`, or `run`) is explicit; inheritance
   requires a versioned `extends` reference and may not widen the parent grant.
3. Select exactly one mode: `inspect`, `simulate`, `replay`, `execute`, or
   `check`. Keep the envelope, action id, preconditions, and expected outputs
   stable across modes.
4. In `simulate`, disable side effects and return predicted transitions and
   evidence requirements with `simulation: true`, `verified: false`, and
   `evidenceTier: pattern-valid`.
5. In `execute`, use only the inherited grant and verified entrypoint. Record
   commands, MCP/MAF calls, inputs, outputs, environment, diffs, and failures.
6. Give the result to a fresh checker. Only that checker can issue `PASS`,
   `LOOP`, or `HALT`; the surface and maker never self-approve.
7. Append one provenance-linked trail frame and one unexecuted next seed.

## MAF Native and filesystem boundary

Use `maf-workflows` for the PMCR-O role graph and checkpoints, and
`maf-mcp-tools` for separately hosted MCP tools. Use the filesystem capability
for relative, read-only discovery of `.agents/`, `.pmcro/`, provider
projections such as `.claude/`, and project files. A filesystem listing does
not grant write, command, MCP, or deployment authority. The marketplace should
discover a layout first, then activate a separately granted capability.

Run the local contract simulation with:

```bash
python3 scripts/simulate_agent_api.py --request assets/agent-surface-request.json
python3 scripts/validate_surface.py --repo .
```

Read `references/simulation-parity.md` before claiming execution evidence.
