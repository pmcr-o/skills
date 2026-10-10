# Sample prompts

Use these to start the output-conventions skill. Keep them short and concrete.

## Prompt 1 — render console output

```text
Render this planner result as a labelled .NET-style console projection with phase, mode, simulation, verification, evidence, and handoff fields.
```

## Prompt 2 — normalize a handoff

```text
Normalize this skill result into the canonical SkillOutput envelope. Preserve unresolved findings and keep the next seed unexecuted.
```

## Prompt 3 — detect a phase jump

```text
Check whether this output skips PLAN, MAKE, CHECK, or REFLECT. Return a typed denial if the handoff is not allowed by the PMCR-O phase order.
```
