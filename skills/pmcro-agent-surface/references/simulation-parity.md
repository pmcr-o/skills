# Simulation parity

Simulation is useful because the same activation envelope can be inspected by
an agent, a MAF workflow, a catalog MCP server, or a local script. It is not
runtime proof.

Every simulation response must include:

```json
{
  "mode": "simulate",
  "simulation": true,
  "verified": false,
  "evidenceTier": "pattern-valid",
  "predictedTransitions": [],
  "requiredEvidence": []
}
```

An execution trace is comparable only when it retains the same action ids,
inputs, dependency refs, expected outputs, and grant. The checker compares the
prediction and the real result, then routes drift to `LOOP` or `HALT`. A
simulated MAF executor, filesystem listing, MCP call, terminal command, or
third-party model remains `simulation=true` unless that exact external action
was independently checked.
