---
name: pmcro-generic-crud
description: Apply a bounded create/read/update/delete contract to declarative PMCR-O resources such as skills, plugins, agent surfaces, memory records, catalog entries, and trails. Use as the generic foundation before composing MAF workflows; simulate first, version updates, and revoke instead of physically deleting by default.
---

# PMCR-O generic CRUD

Use one resource contract for marketplace and agent-surface operations. The
resource may be a skill, plugin, agent, memory record, catalog entry, trail, or
  a .NET domain object derived from `PmcroResource<TId,TVersion>`, or a Clean
  Architecture entity derived from `EntityBase`. The operation
and grant must be explicit.

This is the universal lifecycle lens for skills and agents: create a staged
candidate, read an authorized projection, update by version, and delete by
revoke/tombstone policy. It organizes domain behavior without pretending that
specialized actions such as check, compile, send, or calculate are generic CRUD
operations.

## Safe meanings

- `create`: stage a new version; never publish automatically.
- `read`: return only the requested progressive-disclosure projection.
- `update`: create a new version linked to the predecessor and check the
  expected version; never silently overwrite.
- `delete`: revoke or tombstone by default. Physical deletion requires an
  explicit retention/deletion policy and an independent checker.

Use the canonical CRUD request in `templates/crud-envelope.json` and return a
`SkillOutput` envelope from `templates/skill-output-envelope.json`. In
`simulate`, no file, service, MAF, MCP, or catalog mutation occurs.

Run the local simulation:

```bash
python3 scripts/simulate_crud.py assets/create-request.json
python3 scripts/simulate_crud.py assets/delete-request.json
```

The first response is a staged create; the second is a revoke/tombstone plan.
Both are `simulation=true` and `verified=false`. Use
`assets/PmcroResource.cs` as the PMCR-O resource pattern and
`assets/CleanArchitectureEntityRepository.cs` as the Clean Architecture
domain/application/infrastructure pattern. `EntityBase` assigns
`Guid.NewGuid()` for new entities, `IGenericRepository<TEntity>` constrains
`TEntity : EntityBase`, and the generic implementation can therefore use
`entity.Id` without duplicating an ID contract. Read
`references/crud-contract.md` before adding a real adapter.

Use `IUnitOfWork.Repository<TEntity>()` when an application service needs a
repository for a new entity type. The type constraint supplies the CRUD port
without creating another repository interface. `SaveChangesAsync` is the
commit boundary for a real infrastructure adapter; the included in-memory
coordinator is only a dependency-free contract example.
