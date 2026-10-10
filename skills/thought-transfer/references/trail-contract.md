# Trail contract

Use one JSON object per line for append-only events. At minimum include:

```json
{
  "eventId": "unique-id",
  "parentId": "parent-id-or-null",
  "phase": "orchestrate|plan|make|check|reflect",
  "role": "declared-role",
  "principal": "entrypoint-principal",
  "contextId": "fresh-context-identifier",
  "action": "observable-action",
  "charter": {
    "domains": [],
    "paths": [],
    "tools": [],
    "maxTurns": 1,
    "maxDepth": 0,
    "sideEffects": "none"
  },
  "evidence": {},
  "status": "open|complete|blocked|loop"
}
```

Append the event only after the action or decision is observable. A Git reference can identify an artifact checkpoint, but it cannot replace the principal, charter, or evidence fields.

For a checker event, include `freshContext: true`, the acceptance contract, a finite stop cap, and the verdict. Do not let the checker silently repair the maker artifact.

Replay is read-only: inspect a previous checkpoint or branch from it with a new charter. Do not rewrite an old verdict or infer old authority.

## Phase route and next-seed levels

The control plane admits only this normal route:

```text
ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT
```

Cross-session handoffs carry validated resource references rather than an implicit full transcript. A reflective seed is a prompt intent and remains unexecuted:

```json
{
  "level": "meta|meta-meta|meta-meta-meta",
  "promptIntent": "one bounded next request",
  "requiredResources": ["package-id or trail-event-id"],
  "unexecuted": true
}
```

Use `meta` for an artifact or phase repair, `meta-meta` for a skill/workflow repair, and `meta-meta-meta` for an orchestrator, agent-surface, or prompt-system repair. The orchestrator decides whether to open the next cycle.
