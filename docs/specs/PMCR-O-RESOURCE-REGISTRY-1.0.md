# PMCR-O Resource Registry 1.0

Status: candidate specification

## Purpose

Define how agents, skills, capabilities, transports, model bindings, and projections become planner-admissible resources without conflating creation, checking, registration, and use.

## Lifecycle

`CREATE -> generated-unchecked -> CHECK -> checked-candidate -> REGISTER -> registered-checked -> later USE`

Revocation is append-only and changes planner admissibility without erasing source or checker provenance.

## Normative rules

1. Registry records MUST conform to `.pmcro/protocol/registry-record.schema.json`.
2. `generated-unchecked` resources MUST NOT be planner-admissible.
3. `checked-candidate` resources MUST NOT be planner-admissible until registration exists.
4. `registered-checked` resources MUST carry checker and registration references and MAY be selected by Planner subject to the current plan and grant.
5. `revoked` resources MUST NOT be planner-admissible and MUST preserve their historical registration and revocation references.
6. Planner validated references MUST contain a canonical `registryRef`.
7. Registration MUST NOT widen the caller's grant or convert transport/model availability into execution authority.
8. Registry resolution is read-only and MUST NOT invoke the resolved capability.
9. Producer identity and independent checker identity SHOULD remain distinguishable in evidence.
10. Content digests SHOULD be stable over canonical bytes or a canonical tree digest.

## Skill Creator boundary

Skill Creator owns CREATE for canonical skill candidates. CREATE does not imply READ, UPDATE, DELETE, REGISTER, INSTALL, PUBLISH, or USE. Those lifecycle operations require separately registered authority where implemented.

## Planner rule

Planner selects the minimum sufficient graph from `registered-checked` resources only. A missing or revoked resource remains a capability gap and routes through the normal gap-resolution lifecycle rather than being invented or silently reactivated.
