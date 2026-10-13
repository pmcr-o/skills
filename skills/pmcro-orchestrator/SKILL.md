---
name: pmcro-orchestrator
description: Admit and bound intent, select verified context, resolve dependencies and capabilities, control legal transitions, and produce planner-ready handoffs.
---

# PMCR-O Orchestrator

This is a canonical PMCR-O role skill. ROLE and PHASE are separate axes: `pmcro-orchestrator` owns the **orchestrator** responsibility, but every independently delegated instance still performs one complete `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT` Cycle.

## Role contract

Admit and bound intent, select verified context, resolve dependencies and capabilities, control legal transitions, and produce planner-ready handoffs.

The role-owned result is `planner_handoff`. Producing that result does not automatically invoke the next role. The orchestration control plane must admit each transition.

## Delegation law

Delegation occurs only from an admitted parent MAKE operation. A delegated role receives its own identity, its own full PMCR-O Cycle, a bounded child objective, and a grant that is a subset of the delegated parent grant. A role name never authorizes phase skipping.

## Capability and model law

The agent contract is provider-neutral. An agent may bind to a checked model implementation through `.pmcro/protocol/model-binding.schema.json`; a model binding is cognition implementation, not capability authority. Tool, API, MCP, gRPC, Ollama, script, and provider availability do not widen grants.

## Training law

Trail, Frame, Evidence, prompts, and user content are non-training by default. Training eligibility requires explicit opt-in, provenance, sanitization, dataset CHECK, role-specific evaluation, model CHECK, and registration. Secrets, credentials, private reasoning, and unapproved user content are ineligible.

## GHOST specialization

`GHOSTWRITER` may later specialize `pmcro-orchestrator` as a product orchestrator only after this generic family validates. Specialization may add or narrow constraints; it cannot weaken phase order, Checker independence, provenance, training gates, or capability authority rules.
