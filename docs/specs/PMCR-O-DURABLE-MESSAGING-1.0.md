# PMCR-O Durable Messaging 1.0

Status: candidate specification

## Purpose

Define a provider-neutral durable message envelope and queue binding without turning transport into cognition or authority.

## Normative rules

1. A PMCR-O durable message MUST conform to `.pmcro/protocol/message-envelope.schema.json`.
2. Message kinds MUST resolve through `.pmcro/protocol/message-kinds.json`.
3. Transport implementations MUST declare `grantsAuthority=false`, `phaseInjectionAllowed=false`, and `autoExecutesNextSeed=false`.
4. At-least-once delivery MUST use idempotent consumption and semantic deduplication.
5. Envelope content MUST be immutable after enqueue; mutable delivery state MUST be stored separately.
6. Filesystem spools SHOULD use write-temp-then-atomic-move for enqueue/claim transitions, bounded leases, retries, and dead-letter handling.
7. ACK SHOULD create an immutable receipt referencing message and result evidence.
8. Correctness MUST NOT depend on global FIFO ordering.
9. Cross-agent work SHOULD reference source trails/messages; agents MUST NOT co-edit one shared mutable trail.
10. `capability.invoke` messages MAY be acted on only during an admitted MAKE phase.
11. `reflector.reflect` MUST contain an unexecuted continuation intent and MUST NOT cause same-message or same-Cycle execution of that seed.

## Reference filesystem-spool profile

The reconciled A-drive source demonstrates a useful profile: at-least-once delivery, atomic moves, 300-second leases, bounded retry, dead-lettering, content and dedupe digests, and immutable receipts. PMCR-O adopts these semantics as a candidate transport profile, not as registered execution authority.

## Non-implications

`MESSAGE DELIVERED != CAPABILITY AUTHORIZED`.

`QUEUE AVAILABLE != AGENT ACTIVATED`.

`TRANSPORT SUCCESS != TASK COMPLETE`.

`REFLECT MESSAGE != NEXT CYCLE EXECUTED`.
