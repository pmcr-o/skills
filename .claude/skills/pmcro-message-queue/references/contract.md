# Durable message queue contract

Canonical basis: `docs/specs/PMCR-O-DURABLE-MESSAGING-1.0.md`, `.pmcro/protocol/message-envelope.schema.json`, `.pmcro/protocol/message-kinds.json`, `.pmcro/protocol/transport-binding.schema.json`, and read-only source evidence from `A:/marketplace/eng/install-message-queue.py`.

The queue is a transport adapter, not an authority source. Envelopes are immutable after enqueue. Delivery state lives separately under `state/`. Filesystem moves on one queue root provide the atomic claim boundary. Delivery is at-least-once, so consumers must be idempotent.

`dedupeDigest` protects semantic identity while `contentDigest` protects the exact immutable envelope body. Reusing a message ID with the same semantic body is idempotent; reusing it with different semantic content is a conflict.

Processing state carries a lease. Expired leases are recovered into delayed retry or dead-letter when the bounded attempt count is exhausted. ACK moves the envelope to completed and creates one immutable receipt. NACK never edits the envelope.

Each agent owns a local trail. Cross-agent envelopes reference `trailId` and `cycleId`; they do not create a shared mutable trail. `pmcro.seed` and reflected next-seed payloads remain data until a separately admitted future Cycle begins at ORCHESTRATE.

Manual and agent callers use the exact same `scripts/queue.py` commands. Exit status and JSON output are evidence surfaces. This candidate is not registered merely because isolated fixture tests pass.
