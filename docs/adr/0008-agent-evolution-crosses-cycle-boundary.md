# ADR-0008: Agent evolution crosses a Cycle boundary

Status: accepted

## Context

PMCR-O may improve a custom agent by refining instructions, context, skill composition, capability bindings, policies, evaluations, or model bindings. Immediate use of a newly generated candidate would collapse creation, checking, registration, and execution into one trust boundary.

## Decision

Agent evolution objectives are `CREATE`, `OPTIMIZE`, `ENHANCE`, `REFINE`, or `SPECIALIZE`. Every evolution output begins as `generated-unchecked` and is unavailable to the Planner.

Independent CHECK may produce a checked candidate, but checked state alone does not make the candidate available. Registration is a distinct lifecycle transition. Only a registered candidate may become available to a later Cycle.

REFLECT MUST emit exactly one unexecuted next-seed intent. It MUST NOT reactivate MAKE in the same Cycle. The next seed begins a fresh Cycle at ORCHESTRATE.

## Consequences

The marketplace can improve itself recursively without uncontrolled same-Cycle self-modification. Each Cycle consumes only the previously verified marketplace state and may leave a better verified state for subsequent Cycles.
