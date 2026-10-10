---
name: pmcro-output-conventions
description: Render every PMCR-O skill handoff through one typed output envelope with JSON, trail, and .NET-console projections. Use when chaining skills in a MAF Native workflow or showing a simulated planner/maker/checker result; simulation output never proves runtime execution.
---

# PMCR-O skill output conventions

Give every skill a predictable handoff. The canonical form is the
`templates/skill-output-envelope.json` shape; human console text and trail
frames are projections of that envelope, not separate sources of truth.

## Required output

Include:

- identity: `messageId`, `traceId`, parent, sender, receiver, phase, and mode;
- state: `status`, `simulation`, `verified`, and `evidenceTier`;
- contract: `input`, `output`, `accept`, `deny`, and evidence refs;
- handoff: next skill/role, bounded limits, and one unexecuted seed when needed.

Use `simulate` for a `.NET` console-style demonstration. It must show the same
fields as JSON and say `SIMULATION: true`, `VERIFIED: false`. Do not describe a
predicted command, MAF executor, MCP call, or service result as if it ran.

## MAF chain

Wrap each skill as a typed executor and connect only declared edges. Keep the
public phase graph `orchestrate -> plan -> make -> check -> reflect`; a skill
dependency is not permission to skip a phase. Checkpoints belong to the MAF
workflow runtime, while the output envelope and PMCR-O trail remain the
portable evidence boundary.

Render the example manually:

```bash
python3 scripts/render_console.py assets/planner-simulation.json
```

Read `references/envelope.md` and `references/maf-chain.md` when adding a new
skill, output profile, or workflow edge.
