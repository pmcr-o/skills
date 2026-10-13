# PMCR-O Agent Evolution 1.0

## Status

Normative candidate specification for deterministic conformance.

## Purpose

Agent evolution lets the marketplace improve a custom or generic agent without treating generation as trust or model training as the default optimization mechanism.

## Evolution objectives

An evolution candidate MUST declare exactly one objective: `CREATE`, `OPTIMIZE`, `ENHANCE`, `REFINE`, or `SPECIALIZE`.

Changes MAY target instructions, context, skill bindings, capability bindings, policies, evaluations, or model bindings. Model training is not implied by any evolution objective.

## State machine

`generated-unchecked -> checked-candidate -> registered -> later Cycle use`

A `generated-unchecked` candidate MUST have `availableToPlanner=false`, no checker verdict, no registration reference, and `nextCycleUseAllowed=false`.

A `checked-candidate` MUST carry checker evidence but MUST remain unavailable to the Planner until a separate registration transition occurs.

A `registered` candidate MUST carry checker and registration references and MAY set `availableToPlanner=true` and `nextCycleUseAllowed=true`.

## Optimization order

Implementations SHOULD prefer the least expensive evidence-backed improvement before model training: instruction refinement, context refinement, skill composition, capability composition, policy/grant refinement, tool/transport refinement, evaluation refinement, model selection, adapter/fine-tuning, then specialized training.

## Cycle boundary

REFLECT MUST emit exactly one unexecuted next-seed intent and MUST NOT reactivate MAKE in the same Cycle. A newly registered capability may be considered only by a later Cycle beginning at ORCHESTRATE.

## Skill Creator

The registered Skill Creator MAY create or specialize the minimum missing agent/skill package when a validated Planner capability graph declares the gap. Its output is a candidate, never same-Cycle executable authority.

The schemas are `.pmcro/protocol/agent-evolution.schema.json` and `.pmcro/protocol/next-seed-intent.schema.json`.
