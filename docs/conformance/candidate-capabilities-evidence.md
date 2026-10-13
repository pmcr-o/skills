# Candidate capability conformance evidence

Source branch: `pmcro/skill-creator-bootstrap-reconcile`

Recovery base: `6464eb23aad46a23c82a45dfbaf1b6b1f5b57468`

Candidates checked in this Cycle:

- `skills/pmcro-resource-registry`
- `skills/pmcro-message-queue`

Both candidates are `checked-candidate`, remain unavailable to Planner, have no registration reference, and may not be used until a later fresh Cycle performs REGISTER.

## Resource registry evidence

The candidate requires independent `checker.verdict = PASS` evidence before creating a `registered-checked` fixture record. Producer self-certification is rejected. Resolution returns Planner admissibility only for verified, non-revoked state. Revocation appends a new event and preserves prior record/event provenance. Registry verification checks sequence, hash chaining, record digests, and checker-evidence digests.

## Durable message queue evidence

The candidate implements `filesystem-spool-v1` as transport-only behavior. Semantic duplicate enqueue is idempotent; reuse of the same message ID with different semantic content halts. Claiming preserves immutable envelope bytes and places mutable lease state separately. ACK preserves the envelope and creates one immutable receipt. Retry is bounded, exhausted attempts dead-letter, expired leases recover, each receiver owns its local trail, and a reflected next seed remains data rather than executable continuation.

## Deterministic validation

- Focused candidate tests: 6 PASS.
- Resource-registry local tests: 1 PASS.
- Message-queue local tests: 1 PASS.
- Repository suite: 83 PASS.
- Skill Creator suite: 5 PASS.
- Capability route suite: 3 PASS.
- CAPABILITY_IMPORT suite: 3 PASS.
- Structural validator: `PASS: 148 required files, 12 agent surfaces, 222 trail events`.
- JSON parse: 114 files PASS.
- Candidate registration absence check: PASS.
- `git diff --check`: PASS.
- `A:\marketplace` Git-status SHA-256 before and after validation: `dd4c6d8e7df08f5be5cb6dca428cd18bdef1bb16d8475d58b8e61a708362aec2`.

## Authority boundary

This evidence checks candidate behavior only. It does not REGISTER either capability, add either to canonical marketplace/plugin catalogs, make either Planner-admissible, authorize runtime invocation as registered capability, merge `main`, or authorize model training, pulling, binding, or activation.
