# Micro-level MAF skill chaining and console output

Every skill can be treated as a typed executor boundary without making every
skill an independent autonomous agent. The canonical handoff is a
`SkillOutput` envelope. JSON is the machine contract; `dotnet-console` is a
deterministic human projection; `trail` is the append-only evidence projection.

## Chain

```text
orchestrator -> planner -> maker -> independent checker -> reflector
       |             |         |
   catalog       filesystem   MAF/MCP dependencies under explicit grants
```

The public phase graph stays `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`.
The graph may contain micro-skills inside a phase, but a dependency edge cannot
silently skip a phase or turn a simulation into execution.

## Generic CRUD starting point

The `pmcro-generic-crud` skill is the first foundation for resources such as
skills, plugins, agent surfaces, memory records, catalog entries, trails, and
typed .NET domain objects:

| Operation | Default behavior |
|---|---|
| Create | stage a candidate version |
| Read | disclose the smallest authorized projection |
| Update | create a successor linked to the expected predecessor |
| Delete | revoke/tombstone; erase only under explicit policy |

Each operation returns input/output/accept/deny/evidence plus an unexecuted
checker handoff. The local script runs in simulation mode, so even the delete
example produces a tombstone plan and never removes a file.

For a .NET implementation, `assets/PmcroResource.cs` provides the abstract
generic base model `PmcroResource<TId,TVersion>` and an
`IPmcroCrudStore<TResource,TId,TVersion>` contract. The base carries scope,
version, predecessor, lifecycle, and content hash; the store owns persistence,
authorization, audit, and transactions. A stale `expectedVersion` routes to a
bounded `LOOP` rather than silently overwriting the resource.

## `.NET` console profile

The planner fixture can be rendered as:

```text
I AM: pmcro-planner
PHASE: plan  MODE: simulate  STATUS: complete
SIMULATION: true  VERIFIED: false  EVIDENCE: pattern-valid
INPUT: Plan a typed ProjectName.OrchestrationService surface.
OUTPUT: The smallest graph is planner -> maker -> independent checker -> reflector.
I HAND OFF: maker via pmcro-make (unexecuted=true)
```

This is a faithful presentation of the envelope, not hidden reasoning and not
runtime evidence. A future MAF implementation can wrap the same operation in
an executor, checkpoint it, and compare its execution trace with the simulated
action ids and expected outputs.
