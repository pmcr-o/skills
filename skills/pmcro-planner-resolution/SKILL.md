---
name: pmcro-planner-resolution
description: Deterministic candidate capability that builds a minimum PMCR-O capability graph from canonical registered-checked resources while preserving explicit grants and declaring gaps without invoking capabilities.
---
# PMCR-O Planner resolution

This Skill Creator output is a **candidate** operational resolver for Planner. It reads canonical registry state and emits a capability graph; it does not invoke the selected capabilities.

## Required law

- Only `registered-checked`, Planner-admissible, non-revoked canonical resources may be selected.
- Every selected resource must also be explicitly admitted by the supplied grant set.
- Missing, unavailable, or ungranted resources become explicit capability gaps.
- Selection is minimum-sufficient: only requested resources are returned.
- Resolution is read-only and grants no runtime authority.
- A successful resolution does not execute Maker, a transport, or a reflected next seed.

## Run

`python scripts/resolve_plan.py --registry <index.json> --graph-id <id> --goal-ref <ref> --require <resourceId> --grant-ref <resourceId> ...`

Humans and agents use the same script and JSON output.

This package is not Planner-admissible until a later independent registration Cycle.
