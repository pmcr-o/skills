# Clean Architecture generic entity and repository projection

The PMCR-O generic CRUD skill has two related .NET projections:

1. `PmcroResource<TId,TVersion>` models versioned marketplace/control-plane
   resources.
2. `EntityBase` plus `IGenericRepository<TEntity>` models ordinary domain
   entities in a Clean Architecture application.

They share the same typed handoff envelope, but they are not the same domain
type. The first carries PMCR-O scope, lifecycle, predecessor, and content hash.
The second gives application code a stable identity and persistence port.

## Layer placement

| Layer | Type | Responsibility |
| --- | --- | --- |
| Domain | `EntityBase` | Own `Guid Id` and domain identity rules |
| Application | `IGenericRepository<TEntity>` | Depend on CRUD behavior through `where TEntity : EntityBase` |
| Infrastructure | `InMemoryGenericRepository<TEntity>` example | Implement the port; replace with EF Core/Dapper/etc. |
| PMCR-O adapter | `CrudRequest` / `SkillOutput` | Bound scope, mode, evidence, checker, and simulation status |

The base constructor uses `Guid.NewGuid()` for a new entity. A protected
`Guid` constructor is also provided for persistence rehydration and tests.
Because the repository interface constrains `TEntity` to `EntityBase`, any
generic implementation can safely read `entity.Id` without reflection or a
second identity interface.

```csharp
public sealed class GenericRepository<TEntity> : IGenericRepository<TEntity>
    where TEntity : EntityBase
{
    // AddAsync, GetByIdAsync, ListAsync, UpdateAsync, DeleteAsync
}
```

## Unit of Work composition

The application can expose one coordination port and acquire the generic CRUD
surface for any entity that follows the base convention:

```csharp
public interface IUnitOfWork : IAsyncDisposable
{
    IGenericRepository<TEntity> Repository<TEntity>()
        where TEntity : EntityBase;

    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}

public sealed class Customer : EntityBase
{
    public required string Name { get; init; }
}

// Customer automatically has Id and all generic CRUD operations.
var customers = unitOfWork.Repository<Customer>();
await customers.AddAsync(new Customer { Name = "Ada" }, cancellationToken);
await unitOfWork.SaveChangesAsync(cancellationToken);
```

This is the “CRUD for free” effect: any new domain type that derives from
`EntityBase` and is requested through the Unit of Work receives the existing
`AddAsync`, `GetByIdAsync`, `ListAsync`, `UpdateAsync`, and `DeleteAsync`
surface. The new type supplies only its own data and behavior; the generic
constraint supplies identity and the repository port, so no per-entity CRUD
repository is needed for the baseline operations. This does not make
domain-specific queries, aggregate invariants, transaction isolation,
optimistic concurrency, audit, or outbox delivery free; those remain explicit
application/infrastructure decisions.

The same rule applies to an additional requirement: specify only the missing
delta. If the delta is another CRUD-shaped capability, model it as another
typed repository or adapter composed from the same base contract. Reuse the
generic implementation where its invariants fit; introduce a specialized port
only where the domain actually needs different behavior.

## Important boundary

`DeleteAsync` is a repository port operation, not an automatic authorization
decision. For PMCR-O resources, the public `delete` operation remains a
reversible revoke/tombstone plan until retention policy and an independent
checker allow physical erasure. The local fixture is simulation-only:
`simulation=true`, `verified=false`, and no database or service is touched.

The code asset is intentionally dependency-free and was not compiled in this
environment because the .NET SDK is unavailable. A future bounded cycle may
bind the interface to a pinned MAF workflow or a real persistence adapter.
