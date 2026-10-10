# Skill output envelope

The envelope is the default output contract for every local or federated
skill. It keeps machine routing, human display, and trail evidence aligned.

Required fields:

| Group | Fields |
|---|---|
| identity | `messageId`, `traceId`, `parentMessageId`, `from`, `to` |
| execution | `phase`, `mode`, `status`, `simulation`, `verified`, `evidenceTier` |
| contract | `input`, `output`, `accept`, `deny`, `evidence` |
| handoff | `next.action`, `next.unexecuted`, optional `next.seedLevel` |

Allowed phase transitions are:

`orchestrate -> plan -> make -> check -> reflect`

and a checked `LOOP` may route one bounded repair seed back to the orchestrator
for a new plan. A skill can return `blocked` or `halted`; it cannot invent a
new phase. `accept` and `deny` are output claims to be checked, not a grant.

The default profiles are:

- `json`: canonical machine-readable envelope;
- `dotnet-console`: deterministic labelled lines for a console demonstration;
- `trail`: append-only evidence projection with refs, not a second payload.
