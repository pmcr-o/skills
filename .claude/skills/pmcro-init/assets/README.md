# PMCR-O INIT frozen contract assets

These files are byte-preserving mappings of the independently checked PMCR-O INIT v0.2-r1 candidate from CHECK-028. They are canonical skill assets, not provider authority.

- `schemas/`: JSON Schema 2020-12 contract surfaces.
- `state-machine/`: INIT bootstrap state machine. Its `canonicalCognition` remains ORCHESTRATE → PLAN → MAKE → CHECK → REFLECT.
- `conformance/`: frozen conformance vectors.
- `proto/`: provider-neutral protobuf contract.

The mapping and source hashes are recorded in `.pmcro/evidence/pmcro-init-materialization.json`. `trainingEligible` remains false and the skill remains unregistered.
