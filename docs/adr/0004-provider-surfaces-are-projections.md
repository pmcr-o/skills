# ADR-0004: Provider surfaces are projections, not canonical authority

Status: accepted

## Context

PMCR-O must run across provider-specific repository layouts without allowing each provider tree to become a separate source of truth.

## Decision

Canonical marketplace and plugin authority lives in `.pmcro-plugin/` plus the `.pmcro/` control plane and portable `skills/` packages. Provider-native outputs such as `.agents/`, `.claude/`, and `.claude-plugin/` MUST be generated or reconciled projections. A provider projection MUST NOT widen grants, invent capabilities, override canonical lifecycle state, or self-promote.

## Consequences

Projection compilers require deterministic inputs, provenance, tests, and independent CHECK before promotion. Provider layouts may be regenerated without changing canonical semantic authority.

## Supersedes

None.
