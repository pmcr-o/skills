---
name: pmcro-init
description: Bootstrap PMCR-O project/trail/host context from verified bounded state without becoming a cognitive phase, role, registration action, or authority source.
---

# PMCR-O INIT v0.2-r1

`pmcro-init` materializes the independently checked INIT bootstrap contract. Canonical skill authority lives here under `skills/pmcro-init/`; `.agents` and Claude surfaces are generated projections only.

## Cognitive boundary

INIT is **not** a sixth PMCR-O cognitive phase and is **not** a sixth top-level PMCR-O role. The immutable cognitive sequence remains:

`ORCHESTRATE → PLAN → MAKE → CHECK → REFLECT`

A skill-local bootstrap agent may reason through that normal five-phase cognition while establishing or resuming bounded project/trail/host context.

## Entrypoint

Canonical ingress is `@orchestrator /pmcro:init`. Raw intent ingress remains `@orchestrator /pmcro:seed`; seed ingress does not inject phase state.

## Verified contract

The CHECK-028 v0.2-r1 semantics are mapped without contract changes:

- `assets/schemas/` — typed INIT, authority, environment, host, projection, cognition, continuation, and resume/rebind contracts.
- `assets/state-machine/init-v0.2.machine.json` — bootstrap states and immutable cognition.
- `assets/conformance/init-v0.2.vectors.json` — checked host/adversarial vectors.
- `assets/proto/pmcro_init_v0_2.proto` — provider-neutral wire contract.
- `scripts/contract_checks.py` — checked deterministic authority/provenance helpers.
- `tests/test_init_contract.py` — repository-layout execution of the frozen 50-test baseline/regression suite.

## Authority invariants

Host adapters report observations/maxima; they do not author PMCR-O effective grants or cognition. Effective and child grants remain monotonic subsets. Host memory is not verified state. Discovery is not registration. Transport is not authority. Sandbox availability is not permission. Resume requires principal/authority/environment/capability/conformance rebind. Serialization must match the cognitive frame and provenance remains hash-bound.

## Lifecycle state

This materialization is `checked-candidate` only after the independent materialization Checker passes. It is not Planner-admissible, registered, merged, activated, or usable in this Cycle. CHECK-028 explicitly preserved `trainingEligible=false`, `registrationState=UNREGISTERED`, and `activation=NONE`.

REGISTER is a separate lifecycle authority. Even after a future registration PASS, first USE must occur in a fresh later Cycle. This skill cannot self-register, self-activate, widen grants, or opt itself into training.

## Handoff

Return the INIT frame/status and evidence refs only. Preserve `trainingEligible=false`; preserve the five-phase cognition; stop on missing authority, provenance, or conformance evidence. Do not consume a reflected next seed automatically.
