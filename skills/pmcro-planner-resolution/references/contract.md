# Planner resolution contract

Planner resolution is a read-only projection from canonical registry state into the minimum capability graph needed for one admitted goal.

A resource is selectable only when the canonical record is `registered-checked`, `admissibleToPlanner=true`, has no revocation reference, and its exact `resourceId` appears in the current grant set. Registry membership alone never authorizes execution.

The resolver emits `.pmcro/protocol/capability-graph.schema.json` shape. Missing registry records become `skill-create` gaps; non-registered or revoked records become `defer` gaps; resources outside the explicit grant become `deny` gaps.

Resolution itself does not call selected scripts, tools, transports, models, or future seeds.
