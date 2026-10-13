# ADR-0003: Capability calls occur only in MAKE

Status: accepted

## Context

PMCR-O separates cognition from effects. Host access, transports, tools, and available binaries do not by themselves grant execution authority.

## Decision

External capability, tool, transport, filesystem, process, or network calls MUST occur only during MAKE and only through admitted capabilities and bounded grants.

PLAN may resolve capabilities but MUST NOT execute them. CHECK evaluates completed evidence and MUST NOT repair. REFLECT emits one unexecuted next-seed intent and MUST NOT execute it.

## Consequences

`COMMAND != TOOL`, `CAPABILITY != TRANSPORT`, and `TRANSPORT_AVAILABLE != EXECUTION_AUTHORIZED` remain enforceable across provider projections.
