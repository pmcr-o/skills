---
name: pmcro-skill-lifecycle
description: Gate PMCR-O skill creation through immutable seed provenance, Skill Creator CREATE authority, independent checking, and post-check marketplace projection.
---

# PMCR-O skill lifecycle

Use this skill at the authoring boundary for a new or reconciled skill.

1. Accept new raw intent through the canonical ingress `@orchestrator /pmcro:seed`. The seed command is request ingress, not a sixth cognitive phase; a bare `/seed` may exist only as a host alias.
2. Preserve the inbound raw seed exactly, hash it, and bind provenance before deriving any candidate intent or manifest. A mid-Cycle seed is preserved/queued as inbound data and cannot inject a phase.
3. Route CREATE to the registered `dotagents-skill-creator` authority. Do not require a second implicit creator.
4. Let PMCR-O execute the lifecycle through `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`; do not jump from seed ingress directly to registration or execution. `@orchestrator /pmcro:init` remains the distinct project/trail/context initialization entrypoint around admitted seed data.
5. Require only the core canonical shape: `SKILL.md` plus `agents/` with at least one PMCR-O agent containing `I AM THE`, `I ORCHESTRATE`, `I PLAN`, `I MAKE`, `I CHECK`, and `I REFLECT`.
6. Treat `references/`, `assets/`, `scripts/`, and `tests/` as optional progressive-disclosure layers. Emit them only when the declared capability/artifact graph needs them; never create empty folders for conformity.
7. Keep generated prompt/assets inert until a registered runtime consumes them. Keep generated scripts/code untrusted until checked and later admitted for execution.
8. Require an independent checker before promotion/registration/use. Creation success is not runtime proof.
9. Keep READ/RETRIEVE, UPDATE, DELETE, VERSION, INSTALL, PUBLISH, and EXECUTE as separately registered lifecycle capabilities when available.
10. Register marketplace/provider projections only after the canonical child has checker evidence.
11. Reflection emits one unexecuted next seed; the next Cycle starts again at ORCHESTRATE. REFLECT never reactivates MAKE in the same Cycle.
12. When a validated Planner capability graph declares missing behavior, Maker may invoke the registered Skill Creator only to create or specialize the minimum candidate needed to fill that gap.
13. A generated or checked candidate remains unavailable to Planner selection until registration; only a later Cycle may use the registered capability.

The canonical seed envelope schema is `.pmcro/protocol/seed-envelope.schema.json`. A child may specialize the generic shape for .NET, Docker, MAUI, MCP, Desktop Commander, documentation, prompt templates, or another domain. Specialization adds typed behavior; it cannot widen authority or turn a maker into its own checker.

Simulation must be labeled `simulation: true` and `verified: false`. Generated candidates remain `generated-unchecked` until independent evidence changes that state.
