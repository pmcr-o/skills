# Runtime mapping: PMCR-O, MAF Workflow, CodeAct, Harness, and MCP

The runtime names describe different concerns. They should compose around the
PMCR-O contract instead of replacing its phases.

| Concern | Maps to PMCR-O | Responsibility | Does not provide |
| --- | --- | --- | --- |
| Orchestrator | `ORCHESTRATE` | Own charter, scope, caps, route, and next action | Implementation or self-verdict |
| Planner | `PLAN` | Produce the smallest graph and acceptance evidence | File/tool execution |
| MAF `WorkflowBuilder` | Role graph across `PLAN`/`MAKE`/`CHECK`/`REFLECT` | Connect typed executors, edges, outputs, checkpoints, and resume | Policy authority or checker independence by itself |
| CodeAct-style executor | Usually `MAKE`; optionally a bounded worker in other phases | Execute declared code/tool actions inside a grant and return evidence | Permission to widen scope or certify its own work |
| Harness | Host boundary around every phase | Enforce sandbox, tool grants, budgets, identity, telemetry, cancellation, and process lifecycle | Domain intent or a PMCR-O verdict |
| MCP server/tool | Capability boundary inside a worker/harness | Expose typed external actions and results | Phase routing, promotion, or trust by connection alone |
| Independent checker | `CHECK` | Re-read contract, run proofs in fresh context, issue `PASS`/`LOOP`/`HALT` | Editing the maker artifact |
| Reflector | `REFLECT` | Preserve evidence, derive earned constraint, emit one unexecuted next seed | Executing its own next seed |

## Correct composition

```text
PMCR-O charter
      |
MAF WorkflowBuilder graph
      |
Harness policy/sandbox
      |
CodeAct executor ---- MCP typed tools/filesystem
      |
SkillOutput + checkpoint + trail evidence
      |
fresh checker -> reflector -> unexecuted next seed
```

If a CodeAct-style agent is implemented as a MAF executor, its output must be
the same `SkillOutput` envelope as a non-CodeAct worker. The harness supplies
the action boundary; MAF supplies graph execution and checkpointing; MCP
supplies typed capabilities; PMCR-O supplies phase meaning, evidence, and
promotion rules.

MAF checkpoints are operational recovery artifacts. The PMCR-O trail remains
the portable governance/evidence record. A resumed workflow must preserve the
same executor identities and graph topology before it can continue.

The mapping is a declarative pattern in this repository. It does not claim
that a live MAF host, CodeAct runtime, Harness implementation, or MCP server
was started.
