# PMCR-O Validated Capability Graph 1.0

## Status

Normative candidate specification for deterministic conformance.

## Purpose

The capability graph is the Planner-owned proof that a proposed Maker plan uses the minimum sufficient set of registered, independently checked agents and skills needed for an admitted goal.

## Normative requirements

1. The graph MUST identify the admitted goal and the validated catalog snapshot used for planning.
2. Every selected agent and skill MUST have `validationState = registered-checked` and an evidence reference.
3. The Planner MUST select the minimum sufficient capability set and MUST record minimality evidence.
4. Missing functionality MUST be represented as a capability gap; it MUST NOT be invented from host, shell, model, network, or transport availability.
5. `goalExecutionEligible` MUST be false while any capability gap remains.
6. A gap MAY be resolved by `skill-create`, `agent-specialize`, `defer`, or `deny`.
7. A `skill-create` or `agent-specialize` resolution MAY produce a bootstrap plan only when a registered Skill Creator is already available to the Maker.
8. The bootstrap plan creates a candidate; it does not execute the missing functionality.
9. Newly created capability MUST remain unavailable to the Planner until independent CHECK and registration complete.
10. Provider projections MUST NOT widen the capability graph or infer authority from provider-native tools.

## Planner output

The Planner SHOULD emit `capability_graph`, `capability_gaps`, `dependency_graph`, `maker_handoff`, and acceptance criteria together so the Maker can execute without hidden assumptions.

## Lifecycle

`VALIDATED CATALOG -> MINIMUM CAPABILITY GRAPH -> MAKER PLAN -> CANDIDATE OR RESULT -> CHECK -> REGISTER -> LATER CYCLE USE`

The schema is `.pmcro/protocol/capability-graph.schema.json`.
