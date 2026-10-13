# ADR-0002: Role is not cognitive phase

Status: accepted

## Context

PMCR-O has durable role identities such as Orchestrator, Planner, Maker, Checker, and Reflector, while every agent internally traverses the same cognitive Cycle.

## Decision

A role MUST NOT be treated as a phase. Every PMCR-O agent keeps its durable identity while traversing `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`.

Delegation to another role creates a child Cycle. A role-owned output does not automatically invoke the next role.

## Consequences

Role specialization can evolve independently without changing the cognitive protocol. Provider runtimes may project roles differently, but they cannot collapse durable identity into a single phase.
