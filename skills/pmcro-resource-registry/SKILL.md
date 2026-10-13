---
name: pmcro-resource-registry
description: Provider-neutral candidate capability for content-addressed PMCR-O resource registration, revocation, verification, and Planner-safe resolution. Use only after lifecycle registration; this package is currently a checked candidate and is not Planner-admissible.
---
# PMCR-O resource registry

This skill implements the accepted PMCR-O resource-registry contract with one shared script surface for agent and manual use.

## Authority

The package is a **generated candidate** until independent validation evidence is attached. Its existence or self-tests do not make it available to Planner. Registration remains a later fresh-Cycle operation.

## Operations

- `register`: store a content-addressed resource only when independent `checker.verdict = PASS` evidence is supplied and the checker differs from the producer.
- `resolve`: return Planner admissibility only for a verified, non-revoked `registered-checked` record.
- `revoke`: append a revocation event without deleting provenance.
- `verify`: verify event ordering, hash chaining, record digests, and checker evidence digests.

## Run

```text
python scripts/registry.py <register|resolve|revoke|verify> ...
```

Agents and humans MUST invoke the same script with the same arguments and observe the same exit codes and JSON evidence.

## Invariants

`CREATE != CHECK != REGISTER != USE`. Registry membership does not widen grants, transport does not create authority, revocation preserves history, and a producer cannot independently certify its own resource.

See `references/contract.md` for the canonical behavior mapped from `PMCR-O-RESOURCE-REGISTRY-1.0` and the read-only A-drive source evidence.
