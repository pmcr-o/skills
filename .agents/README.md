# Agent surfaces

An agent surface is a declarative description of a role, its entrypoints, its allowed tools, its context boundary, and the evidence it must return. It is not a credential and does not itself grant access.

The files in `.agents/agents/` model the control plane and its phase surfaces:

- `orchestrator.json`: opens a bounded PMCR-O cycle;
- `planner.json`: chooses the bare-minimum graph from validated resources;
- `skill-creator.json`: turns a declarative manifest into a draft skill shape;
- `maker.json`: creates or updates an artifact only within the charter;
- `checker.json`: independently checks a handoff in a separate context;
- `reflector.json`: waits for a completed independent checker frame, invokes the marketplace `reflect` skill, records an earned constraint, and proposes a next seed;
- `progressive-trail-flow.json`: projects checked trails into domain-aware training candidates or forward product handoffs.

The public control-plane order is strict:

```text
ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT
```

The orchestrator owns phase advancement. A receiving session gets only a validated handoff—resource IDs, paths, hashes, commits, evidence, scope, and one unexecuted seed. It requests another package only when a declared resource is unavailable; a full transcript is not the default handoff.

The checker is intentionally independent in context and responsibility. A phase agent can be independent from other phase agents without becoming the checker. Independence is a property of the envelope and evidence path, not a mystical property of the model.

The reflector is not the checker. It waits for the checker frame, appends one
reflection frame, and hands the next seed back to the orchestrator. Each seed
is intentionally messy raw input for the next cycle; the orchestrator
re-derives intent and revalidates resources before PLAN.

Multiple accounts can enter through different principals or plugins. The account identifier is recorded in an envelope, while authorization still comes from the explicit charter and capability grant.
