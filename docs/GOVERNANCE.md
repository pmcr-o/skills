# PMCR-O Governance

PMCR-O governance protects architectural law, marketplace authority, and evidence quality while allowing incremental implementation.

## Decision layers

- Architecture Decisions (ADRs) define durable technical law.
- Specifications define normative behavior with MUST/SHOULD/MAY requirements.
- Schemas define machine-readable contracts.
- Implementations realize those contracts.
- Deterministic tests establish conformance.
- Evidence records observed outcomes.

No implementation, provider projection, model, or transport may silently weaken an accepted ADR or normative specification.

## Change classes

Routine implementation changes MAY proceed inside an existing accepted contract when tests and evidence remain green.

Changes that alter phase order, authority, marketplace hierarchy, capability lifecycle, checker independence, training-data eligibility, provider-projection authority, secret handling, or model lifecycle require an ADR proposal or an explicit superseding ADR.

## Promotion

Creation, import, compilation, generation, or successful invocation is not promotion evidence. Registration and promotion require independent CHECK evidence against declared acceptance criteria.

## Provider projections

Provider-specific files are projections. A provider projection MUST NOT become independently authoritative. Drift between canonical PMCR-O contracts and projections is a conformance defect.

## Training and models

Dataset eligibility, model training, model registration, agent binding, and model activation are separate lifecycle stages. A checked dataset does not authorize training. A trained model does not authorize registration. A registered model does not grant capability authority.

## Evidence

Failures, blocked states, and rejected transitions remain evidence. CHECK does not erase failures by repairing work in place. Corrections begin through a later admitted Cycle.
