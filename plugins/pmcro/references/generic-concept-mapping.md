# Generic concept mapping reference

Load this reference when one PMCR-O concept must be projected into multiple
languages, repositories, providers, agent hosts, or runtime domains.

The rule is:

```text
concept/invariant -> canonical envelope -> domain adapter -> evidence
```

An adapter may change names, types, storage, or execution mechanisms. It may
not silently change scope, grant, phase meaning, checker independence,
simulation status, or promotion rules. If a field cannot be carried, record
the loss explicitly and route the result to `LOOP`, `ASK`, or `HALT` as the
charter requires.

Use the detailed mapping procedure and examples in
`docs/19-generic-concept-mapping.md`. The Clean Architecture projection is in
`docs/17-clean-architecture-generic-repository.md`; the MAF, CodeAct, Harness,
and MCP runtime projection is in
`skills/pmcro-clean-architecture/references/runtime-mapping.md`.

The mapping is only as strong as its evidence:

- semantic similarity is not source-code interchangeability;
- structural validity is not runtime execution;
- a simulated workflow is not a verified workflow;
- a connected MCP capability is not automatically trusted;
- a reusable template is promoted only after an independent checker passes.
