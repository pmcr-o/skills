---
name: pmcro-skill-lifecycle
description: Gate every PMCR-O skill lifecycle through a typed skill.create.request, generic required-folder template, message contract, sample prompts, independent checking, and post-check marketplace projection.
---

# PMCR-O skill lifecycle

Use this skill at the authoring boundary for a new or reconciled skill.

1. Emit one `skill.create.request` through `@skill-creator /create-skill`.
2. Validate the source intent, scope, resources, required shape, message
   contract, sample-prompt reference, and simulation/apply mode.
3. Let PMCR-O route the request through ORCHESTRATE, PLAN, MAKE, CHECK, and
   REFLECT. Do not jump directly from a prompt to marketplace registration.
4. Require `SKILL.md`, `agents/`, `scripts/`, `references/`, `assets/`, and
   `tests/`, with an agent manifest, validator, asset documentation, and
   bounded copy/paste sample prompts.
5. Register the marketplace projection only after an independent checker.

The child may specialize a generic template for .NET, Docker, MAUI, MCP,
Desktop Commander, or another domain. Specialization adds typed domain
behavior; it cannot widen the parent grant or turn a maker into a checker.

Simulation is labeled `simulation: true` and `verified: false`. The next seed
is always unexecuted and must be re-derived by the next orchestrator.
