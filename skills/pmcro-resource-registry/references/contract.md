# Resource registry contract

Canonical basis: `docs/specs/PMCR-O-RESOURCE-REGISTRY-1.0.md`, `.pmcro/protocol/registry-record.schema.json`, `.pmcro/protocol/capability-graph.schema.json`, and read-only source evidence from `A:/marketplace/eng/src/resource-registry/lib/registry_core.py`.

The registry is an admissibility index, not an authority source. A record reaches `registered-checked` only with independent checker PASS evidence. Planner may select only verified, non-revoked `registered-checked` records. Registration does not widen the record's grants.

The event log is append-only and hash chained. REGISTER stores content digest, provenance, producer identity, checker identity, and checker evidence digest. REVOKE changes admissibility without deleting the record or prior event.

Manual and agent callers use the exact same `scripts/registry.py` commands. Exit status and JSON output are part of the evidence surface.

This candidate skill itself is not registered merely because it can manipulate an isolated registry fixture during tests.
