# Trail product schema

Every cycle appends role-owned frames to `.pmcro/trails/`. A product projection
may expose catalog metadata, the contract, evidence, implementation assets, or
an authorized raw trace. It must retain:

- source/ref and integrity hash;
- principal, role, scope, consent, and retention;
- simulation/execution/production evidence tier;
- acceptance checks and the independent checker verdict;
- corrections, earned constraints, and one unexecuted next seed.

Product states are:

`raw -> redacted -> structured -> checked -> staged -> published -> derived`

`published` means catalog-visible under policy; it does not mean all raw frames
are public. A failed or simulated trail can become a counterexample or repair
fixture, but not a successful runtime claim.
