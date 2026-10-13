# ADR-0007: Planner uses a validated capability graph

Status: accepted

## Context

A host may expose many tools, models, binaries, plugins, and transports. Treating physical availability as planning authority would allow PMCR-O to invent or silently assume capabilities.

## Decision

The Planner MUST construct the minimum sufficient plan from a validated agent and capability catalog. Selected agents and skills MUST carry checked registration evidence. Missing functionality MUST be represented explicitly as a capability gap.

A plan with unresolved capability gaps MUST NOT declare the original goal executable. When the registered Skill Creator can legally fill a gap, the Planner MAY emit a bounded bootstrap plan whose objective is candidate creation rather than execution of the original missing functionality.

## Consequences

Planning becomes evidence-backed and minimal. Missing functionality is visible instead of hallucinated. Skill Creator becomes the registered CREATE path for capability gaps without granting the generated child same-Cycle execution authority.
