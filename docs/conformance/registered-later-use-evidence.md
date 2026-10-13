# Registered later-use evidence

Source commit: `a76d484fd53fa2c094fb2bc5fc12e2abeab68853`

The first bounded later-use exercise resolved the already registered `pmcro-resource-registry` and `pmcro-message-queue` resources from canonical registry state, preserved the explicit grant set, registered and resolved one isolated synthetic resource, and moved one immutable `agent.handoff` through enqueue, claim, and ACK.

Observed transport properties were preserved: semantic duplicate enqueue was idempotent, claim did not change immutable envelope bytes, ACK emitted an immutable receipt, source trail reference and receiver-local-trail result digest remained available as evidence, transport granted no authority, and the reflected next-seed string remained unexecuted payload data.

## Conformance blocker

The exercise also exposed a real defect in the registered queue v1. `.pmcro/protocol/message-envelope.schema.json` requires `transportContext`, but `skills/pmcro-message-queue/scripts/queue.py` does not currently place that field in the emitted immutable envelope. The functional round-trip therefore does **not** establish full canonical message-envelope conformance.

This evidence is intentionally `INCOMPLETE`, not silently upgraded to PASS. Repairing the queue implementation changes registered content and therefore requires a checked replacement plus a later registration Cycle before the repaired version can be used.

The same Cycle created and independently checked `pmcro-planner-resolution` as an unregistered candidate. It performs deterministic, read-only, minimum-sufficient registry resolution with explicit grant preservation and never invokes selected capabilities. It remains unavailable until a later REGISTER Cycle.
