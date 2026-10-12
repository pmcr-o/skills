---
name: pmcro-skill-lifecycle
description: Gate PMCR-O skill creation through immutable seed provenance, Skill Creator CREATE authority, independent checking, and post-check marketplace projection.
---

# PMCR-O skill lifecycle

Use this skill at the authoring boundary for a new or reconciled skill.

1. Preserve the inbound raw seed exactly and bind provenance before deriving a candidate manifest.
2. Route CREATE to the registered `dotagents-skill-creator` authority. Do not require a second implicit creator.
3. Let PMCR-O execute the lifecycle through `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`; do not jump from a prompt directly to registration or execution.
4. Require only the core canonical shape: `SKILL.md` plus `agents/` with at least one PMCR-O agent containing `I AM THE`, `I ORCHESTRATE`, `I PLAN`, `I MAKE`, `I CHECK`, and `I REFLECT`.
5. Treat `references/`, `assets/`, `scripts/`, and `tests/` as optional progressive-disclosure layers. Emit them only when the declared capability/artifact graph needs them; never create empty folders for conformity.
6. Keep generated prompt/assets inert until a registered runtime consumes them. Keep generated scripts/code untrusted until checked and later admitted for execution.
7. Require an independent checker before promotion/registration/use. Creation success is not runtime proof.
8. Keep READ/RETRIEVE, UPDATE, DELETE, VERSION, INSTALL, PUBLISH, and EXECUTE as separately registered lifecycle capabilities when available.
9. Register marketplace/provider projections only after the canonical child has checker evidence.
10. Reflection emits one unexecuted next seed; the next Cycle starts again at ORCHESTRATE.

A child may specialize the generic shape for .NET, Docker, MAUI, MCP, Desktop Commander, documentation, prompt templates, or another domain. Specialization adds typed behavior; it cannot widen authority or turn a maker into its own checker.

Simulation must be labeled `simulation: true` and `verified: false`. Generated candidates remain `generated-unchecked` until independent evidence changes that state.
