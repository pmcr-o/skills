# ADR-0010: Registry state controls planner admissibility

Status: accepted

## Context

The A-drive marketplace separates resource registration, resolution, revocation, checker evidence, and append-only provenance. The current PMCR-O capability graph already requires registered checked resources, but did not yet bind that requirement to a canonical registry record.

## Decision

A Planner MAY select a resource only when its canonical registry record is `registered-checked`, non-revoked, provenance-preserving, and backed by an independent checker verdict and registration reference. Generated or merely checked candidates remain unavailable to planning until registration. Revocation removes admissibility without deleting historical provenance.

Registration never widens a grant. A registered transport, model binding, skill, capability, projection, or agent still requires applicable plan/grant authority before use.

## Consequences

The capability graph now carries a `registryRef` for every validated resource. Skill Creator continues to own CREATE only; READ, UPDATE, DELETE, REGISTER, and USE remain separately authorized lifecycle capabilities. Registry resolution is read-only and is not execution.
