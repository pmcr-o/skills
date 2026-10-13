# Output-convention examples

## Purpose

`planner-simulation.json` demonstrates one typed planner handoff rendered as
JSON and `.NET` console-style text.

## Inputs

`scripts/render_console.py` consumes the `SkillOutput` fixture and requires
identity, phase, simulation, evidence, contract, and next-handoff fields.

## Expected output

The renderer prints `SIMULATION: true`, `VERIFIED: false`, input/output,
accept/deny, evidence, and an unexecuted maker handoff.

## Evidence and limits

This is `pattern-valid` output only. It does not run a planner, MAF executor,
CodeAct worker, MCP tool, or .NET process.
