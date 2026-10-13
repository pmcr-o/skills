---
name: pmcro-message-queue
description: Provider-neutral registered capability for durable PMCR-O message transport over a filesystem spool with immutable envelopes, explicit state, bounded retries, and no authority grant. Use only after later lifecycle registration; this package is not Planner-admissible in its creation Cycle.
---
# PMCR-O message queue

This skill implements the accepted durable-messaging contract with one shared script surface for agent and manual use.

## Authority

The queue is transport only. A message never creates PMCR-O authority, never injects a cognitive phase, and never auto-executes a reflected next seed. This skill remains a candidate until an independent CHECK and a later fresh-Cycle REGISTER operation.

## Operations

- `init`: create an isolated filesystem-spool queue root and transport configuration.
- `enqueue`: write one immutable envelope by temp-file plus atomic move; repeated semantic content with the same message ID is idempotent.
- `claim`: atomically move one available envelope into processing and attach mutable lease state outside the envelope.
- `ack`: move the immutable envelope to completed and create an immutable receipt.
- `nack`: schedule bounded retry or dead-letter after the maximum attempt count.
- `recover`: recover expired leases, release due delayed messages, and dead-letter expired envelopes.
- `verify-message`: verify envelope digests without changing it.
- `stats`: report queue-state counts.

## Run

```text
python scripts/queue.py <init|enqueue|claim|ack|nack|recover|verify-message|stats> ...
```

Agents and humans MUST invoke the same script with the same arguments and observe the same exit codes and JSON evidence.

## Invariants

Delivery is at-least-once, consumers must be idempotent, mutable delivery state is separate from message content, ACK receipts are immutable, each agent owns a local trail, and `TRANSPORT != AUTHORITY`.

See `references/contract.md` for the reconciled contract mapped from `PMCR-O-DURABLE-MESSAGING-1.0` and the read-only A-drive queue source evidence.
