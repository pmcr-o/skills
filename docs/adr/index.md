# Architecture Decision Records

PMCR-O uses Architecture Decision Records for significant technical decisions that constrain marketplace, plugin, agent, skill, capability, model, evidence, training, transport, registry, or provider-projection behavior.

Each ADR contains Context, Decision, Consequences, Status, and Supersedes/Superseded By when applicable.

Allowed statuses are `proposed`, `accepted`, `deprecated`, and `superseded`.

Accepted ADRs are architectural law until explicitly superseded. Implementations and documentation SHOULD link to the ADRs that govern them. Deterministic conformance tests SHOULD exist for machine-enforceable decisions.

## Initial decision set

- ADR-0001: Marketplace is the canonical top-level system.
- ADR-0002: Role is not cognitive phase.
- ADR-0003: Capability and transport calls occur only during MAKE.
- ADR-0004: Provider surfaces are projections, not canonical authority.
- ADR-0005: Trail data is not training data by default.
- ADR-0006: Claude is the reference provider layout.
- ADR-0007: Planner uses a validated capability graph.
- ADR-0008: Agent evolution crosses a Cycle boundary.
- ADR-0009: Durable messages are transport, not cognition.
- ADR-0010: Registry state controls planner admissibility.

New ADRs MUST avoid silently weakening accepted PMCR-O invariants.
