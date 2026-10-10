# Generic CRUD and .NET examples

## Purpose

These fixtures show provider-neutral CRUD, PMCR-O resource versioning, Clean
Architecture identity/repository contracts, and Unit of Work composition.

## Inputs

`create-request.json`, `delete-request.json`, `dotnet-model-request.json`,
`dotnet-clean-architecture-request.json`, and
`dotnet-unit-of-work-request.json` feed `scripts/simulate_crud.py`.
`PmcroResource.cs` models PMCR-O resources. `CleanArchitectureEntityRepository.cs`
models `EntityBase`, `IGenericRepository<TEntity>`, and `IUnitOfWork`.

## Expected output

The simulator returns a `SkillOutput` with explicit operation, scope, version,
architecture projection, artifacts, accept/deny rules, and checker handoff.
Delete produces a revoke/tombstone plan by default.

## Evidence and limits

All fixtures are simulation-only: `simulation=true`, `verified=false`.
The C# examples are documented contract assets; they were not compiled here,
and no database, transaction, MAF workflow, or MCP tool was executed.
