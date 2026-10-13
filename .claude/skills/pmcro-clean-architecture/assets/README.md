# Clean Architecture builder examples

## Purpose

`application-request.json` demonstrates how a .NET application request names
its layers, entities, target framework, source policy, and staged target root.

## Inputs

The simulator consumes the request's application identity, `net8.0` target,
`Customer`/`Order` entities, local-template source, and no-side-effect grant.
`manifest.schema.json` documents the request shape.

## Expected output

`simulate_architecture.py` emits Domain, Application, Infrastructure, API, and
Tests paths plus `EntityBase<Guid>`, `IGenericRepository<TEntity>`,
`IUnitOfWork`, and runtime-adapter mappings.

## Evidence and limits

The output is a `SkillOutput` simulation with `verified=false`. It does not
create a project, run `dotnet build`, install packages, start MAF/MCP, or prove
database behavior.
