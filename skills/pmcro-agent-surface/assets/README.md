# Agent-surface examples

## Purpose

These fixtures teach the scoped agent-surface request and manifest shape.

## Inputs

`agent-surface-request.json` is consumed by `simulate_agent_api.py`.
`manifest.schema.json` describes the required surface fields.

## Expected output

The simulator returns a typed API response with explicit scope, grant,
simulation status, and checker handoff.

## Evidence and limits

The result is `simulation=true`, `verified=false`, and `pattern-valid`. No API,
filesystem mutation, credential, or production agent was started.
