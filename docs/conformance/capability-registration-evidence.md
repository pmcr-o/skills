# Capability registration conformance evidence

Source checked commit: `68ff94f306be9ced7942060838af37514adfe22d`.

Registered resources:

- `skill:pmcro-resource-registry`
- `skill:pmcro-message-queue`

The prior independent Checker artifact remains `.pmcro/evidence/candidate-capabilities-check.json` with SHA-256 `acd373bc292cb5ffbf2c2a1116aacecf9b6793c869453e1e4fd1e6243850cfa5`.

Pre-registration canonical tree digests were `a3ac9c6e61cec75070d61300450c401a7b9fe4cea103acd180d0db9d8fe284b4` for the registry package and `bf25d53faa08b9a8476e3a067b5ae07d08ca7c7252572aad19285526cae09f90` for the queue package. Registration preserves these checked-source digests and records separate registered-state content digests in `.pmcro/registry/index.json`.

Registration changes canonical Planner admissibility only. It does not widen grants, does not consume a reflected seed, and does not perform a Planner/runtime invocation of either registered capability. Conformance fixture execution remains test evidence rather than lifecycle USE. First lifecycle USE is restricted to a fresh later Cycle.

Validated registration properties:

- both registry records are `registered-checked` and Planner-admissible;
- each record is digest-bound to the registered package tree and references independent Checker evidence;
- `filesystem-spool-v1` is `registered-checked` while `grantsAuthority=false` and `autoExecutesNextSeed=false`;
- canonical plugin, legacy compatibility plugin, and `.agents` marketplace projection expose both resources from canonical registration state;
- deterministic Claude projection contains both registered skills while remaining non-canonical and non-authoritative;
- registration-cycle use is false and next-Cycle use is true;
- A-drive source marketplace status remained byte-for-byte unchanged by the Cycle.

Deterministic validation at registration time passed 5 registration tests, 6 candidate behavior tests, 9 registry/queue reconciliation tests, 4 marketplace projection tests, 1 registry package-local test, 1 queue package-local test, 88 repository tests, 5 Skill Creator tests, 3 capability-route tests, 3 CAPABILITY_IMPORT tests, structural validation (`148 required files, 12 agent surfaces, 222 trail events`), 115 JSON parses, and `git diff --check`.

`A:\marketplace` status SHA-256 remained `dd4c6d8e7df08f5be5cb6dca428cd18bdef1bb16d8475d58b8e61a708362aec2` before and after validation.
