# ADR-0009: Durable messages are transport, not cognition

Status: accepted

## Context

The A-drive marketplace contains a mature filesystem-spool queue with immutable envelopes, trace/correlation identifiers, digests, leases, retries, receipts, and at-least-once delivery. Those mechanics are useful, but PMCR-O already distinguishes transport from cognitive phase and authority.

## Decision

PMCR-O adopts the durable-message envelope and transport semantics as transport infrastructure only. Messages MAY carry seeds, handoffs, plans, results, verdicts, reflections, capability calls, and registry events, but message delivery MUST NOT inject ORCHESTRATE, PLAN, MAKE, CHECK, or REFLECT state. A transport MUST declare that it grants no authority and MUST NOT auto-execute a reflected next seed.

`capability.invoke` remains legal only during MAKE. `reflector.reflect` carries exactly one unexecuted continuation intent; a later admitted Cycle begins again at ORCHESTRATE.

## Consequences

Queue implementations may be replaced without changing PMCR-O cognition. At-least-once delivery requires idempotent consumers and deduplication. Transport evidence can support CHECK, but transport success is not task completion or execution authorization.
