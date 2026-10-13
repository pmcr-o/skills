---
name: pmcro-clean-architecture
description: Build a bounded .NET Clean Architecture application plan and staged scaffold from a declarative request. Composes EntityBase, IGenericRepository, IUnitOfWork, infrastructure adapters, API agent surfaces, and PMCR-O evidence; defaults to simulation and requires an exact repository ref before reusing external source.
---

# PMCR-O Clean Architecture builder

Use this skill when a .NET application should follow the user's standard
Clean Architecture shape. The skill is a builder contract, not a claim that a
production application or external repository has already been executed.

## Default composition

```text
Domain -> Application -> Infrastructure -> API/worker
   |          |              |                |
EntityBase  repository     persistence       agent surface
            + UnitOfWork   adapter            + PMCR-O envelope
```

The baseline uses `EntityBase` with `Guid` identity,
`IGenericRepository<TEntity> where TEntity : EntityBase`, and
`IUnitOfWork.Repository<TEntity>()`. Any new entity that derives from
`EntityBase` gets the existing Add/Get/List/Update/Delete CRUD surface through
the Unit of Work. Specify only the entity's missing delta; if an additional
capability is itself CRUD-shaped, compose another typed repository or adapter
from the same contract. Domain rules and specialized queries remain explicit.

## Procedure

1. Preserve the raw request and validate the application name, namespace,
   target framework, entity list, scope, mode, and output profile.
2. Use the local declarative baseline unless the request supplies an exact
   external repository URL, commit/ref, license, and allowed path scope.
3. Plan the smallest layers: Domain, Application, Infrastructure, API or
   worker, tests, and the PMCR-O agent surface. Do not create provider-specific
   copies when an adapter is sufficient.
4. Emit the canonical `SkillOutput` envelope and a `.NET` console projection.
   Simulation is always `simulation=true` and `verified=false`.
5. Apply only to an explicit new or staged target root. Never overwrite an
   unknown existing project, install packages, access credentials, or publish.
6. Hand the result to a separate checker. The checker must validate project
   layout, generic constraints, repository/Unit of Work contracts, source
   provenance, and generated tests before promotion.

Read `references/runtime-mapping.md` when binding the plan to MAF
`WorkflowBuilder`, a CodeAct-style executor, a host Harness, or MCP tools.
These are runtime adapters around the PMCR-O graph, not replacements for its
orchestrator, checker, or reflector roles.

Run the bounded simulation:

```bash
python3 scripts/simulate_architecture.py assets/application-request.json
python3 scripts/validate_architecture.py --repo .
```

## Handoff

Return the architecture plan, source/ref decision, target scope, generated
paths, evidence, unresolved findings, checker handoff, and one unexecuted
next seed. A plan or simulation does not prove that `dotnet build`, a database,
MAF, MCP, or a deployed API ran.

## Refusals

Refuse an unpinned external repository, an ambiguous target root, unknown-file
overwrite, unbounded project generation, secret access, silent package
installation, self-approval, or a claim that generic CRUD replaces domain
invariants and transaction policy.
