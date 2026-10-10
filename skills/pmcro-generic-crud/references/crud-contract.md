# Generic CRUD contract

CRUD is a semantic contract over versioned declarative resources, not a license
to call arbitrary filesystem delete or overwrite commands.

Required request fields are `requestId`, `traceId`, `resource.kind`,
`resource.id`, `resource.scope`, `operation`, `mode`, `projection`, `grant`,
and `outputProfile`.

| Operation | Required evidence | Safe simulation result |
|---|---|---|
| create | schema, parent scope, checker route | `staged`, new candidate version |
| read | disclosure policy, authorization | `disclosed`, bounded projection |
| update | predecessor/version, diff, checker | `versioned`, successor ref |
| delete | retention policy, revocation reason, checker | `revocation-planned`, tombstone |

The output is a `SkillOutput` message with `input`, `output`, `accept`, `deny`,
evidence, and an unexecuted handoff. The resource's scope and the operation's
grant are checked independently. A model request cannot widen either one.

## .NET abstract base model

`assets/PmcroResource.cs` is an implementation-shaped contract for PMCR-O
resources. A concrete model supplies its own `Kind` while inheriting identity,
scope, version, lifecycle, predecessor, and content hash. A typed store can
then expose `CreateAsync`, `ReadAsync`, `UpdateAsync`, and `RevokeAsync` while
the PMCR-O envelope remains unchanged. `expectedVersion` is the optimistic
concurrency boundary; an update against a stale version becomes `LOOP`, not an
overwrite.

For a Clean Architecture domain model, use
`assets/CleanArchitectureEntityRepository.cs`:

```csharp
public abstract class EntityBase
{
    protected EntityBase() : this(Guid.NewGuid()) { }
    protected EntityBase(Guid id) => Id = id;
    public Guid Id { get; private set; }
}

public interface IGenericRepository<TEntity>
    where TEntity : EntityBase
{
    Task<TEntity> AddAsync(TEntity entity, CancellationToken cancellationToken = default);
    Task<TEntity?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<TEntity>> ListAsync(CancellationToken cancellationToken = default);
    Task<TEntity> UpdateAsync(TEntity entity, CancellationToken cancellationToken = default);
    Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default);
}
```

The constraint is the important part: application code can access `entity.Id`
for every `TEntity` without reflection or duplicated interfaces. Infrastructure
can implement the same port with EF Core, Dapper, a document store, or the
dependency-free in-memory sample. Repository `DeleteAsync` is a Clean
Architecture persistence operation; when the resource is a PMCR-O artifact,
the adapter still maps the public `delete` intent to revoke/tombstone unless an
explicit retention policy authorizes physical erasure.

## Unit of Work composition

`IUnitOfWork.Repository<TEntity>()` is the reusable composition point:

```csharp
public interface IUnitOfWork : IAsyncDisposable
{
    IGenericRepository<TEntity> Repository<TEntity>()
        where TEntity : EntityBase;

    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}
```

That means a new `Customer : EntityBase` or `Order : EntityBase` receives the
same typed CRUD port through `unitOfWork.Repository<Customer>()`; the
application does not need a second generic repository interface merely to
obtain `Id`. The infrastructure implementation still owns transaction,
concurrency, persistence, and change-count semantics. The in-memory sample
returns zero from `SaveChangesAsync` because its repository operations are
immediate and it does not pretend to provide database atomicity.

The file is intentionally an asset rather than a runtime dependency. The
application must bind persistence, authorization, serialization, audit, and
transaction behavior before execution evidence exists.
