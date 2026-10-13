# Enterprise memory release gate

Before activating a memory record, verify:

- **Identity:** owner, scope, schema version, purpose, and authorized readers.
- **Provenance:** exact source refs, checker verdict, evidence tier, and hash.
- **Safety:** secret-free content, prompt-injection handling, tool boundaries,
  output validation, rate limits, and no authority encoded in prose.
- **Lifecycle:** retention/expiry, refresh trigger, supersession, revocation,
  deletion behavior, and schema migration plan.
- **Operations:** metrics/traces with sensitive data disabled by default,
  correlation/run ids, error handling, idempotency, backups, restore testing,
  and incident/audit export.
- **Quality:** positive, counterexample, invariant, and escalation cases; a
  bounded eval; regression comparison; and a separate checker.
- **Cost/context:** token budget, retrieval filters, deterministic ordering,
  pagination, cache freshness, and progressive disclosure.

Keep raw trails in a restricted evidence store. Project only the minimum
record needed by the agent. If a source or policy changes, invalidate or route
the record to `LOOP`; do not silently keep stale instructions.
