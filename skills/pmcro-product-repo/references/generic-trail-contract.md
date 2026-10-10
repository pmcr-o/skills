# Generic trail contract

Only the trail protocol is universal. Domain behavior stays in the product's
artifacts, references, adapters, and tests. A generic event records:

- stable trail, cycle, and event identifiers;
- the PMCR-O phase and `I AM` role identity;
- speaker, addressee, and the act that changed shared state;
- scope, artifact references, and evidence references;
- explicit `simulation` and `verified` values;
- status, parent linkage, and an orchestrator-owned next seed.

Trails are append-only and provenance-linked. Preserve raw source separately;
redact secrets, private reasoning, and unauthorized third-party data before a
trail becomes a product. Use progressive disclosure: metadata, contract,
evidence, assets, then an authorized raw trace.

A failed or simulated run remains useful as a counterexample, but it cannot be
reported as successful execution. A checker frame must come from a separate
context and must not be emitted by the maker.
