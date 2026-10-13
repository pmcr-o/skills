# PMCR-O Planner Resolution 1.0

Status: candidate specification

## Purpose

Define deterministic Planner resolution from canonical registry state into the minimum capability graph required by one admitted goal.

## Normative rules

1. Planner MUST resolve capability availability from canonical registry state rather than filesystem presence, transport availability, or provider projection presence.
2. Planner MUST select only `registered-checked`, non-revoked records with `admissibleToPlanner=true`.
3. Every selected resource MUST also be explicitly admitted by the current grant set; registry membership MUST NOT widen grants.
4. Resolution MUST be read-only and MUST NOT invoke the selected capability.
5. Missing resources MUST become explicit capability gaps rather than invented functionality.
6. Unregistered or revoked resources MUST remain unavailable.
7. Ungranted registered resources MUST remain unavailable to the current plan.
8. The selected graph MUST be minimum-sufficient and MUST NOT include unrequested resources merely because they exist in the catalog.
9. Successful resolution MAY make a later Maker invocation eligible but MUST NOT perform that invocation itself.
10. A reflected next seed carried in any queue message remains data until a fresh Cycle is admitted.

## Lifecycle boundary

`REGISTERED-CHECKED -> PLANNER RESOLUTION -> MAKER USE -> CHECK -> REFLECT`

These are distinct transitions. Resolution does not collapse them.

## Candidate implementation

`skills/pmcro-planner-resolution` is a Skill Creator candidate for this specification. It remains unavailable to Planner until an independent CHECK and a later REGISTER Cycle complete.
