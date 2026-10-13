using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ThoughtTransfer.CleanArchitecture;

/// <summary>
/// Domain-layer identity base. New entities get an identity immediately;
/// rehydrated entities may use the protected identity constructor.
/// </summary>
public abstract class EntityBase
{
    protected EntityBase() : this(Guid.NewGuid())
    {
    }

    protected EntityBase(Guid id)
    {
        if (id == Guid.Empty)
        {
            throw new ArgumentException("An entity id cannot be empty.", nameof(id));
        }

        Id = id;
    }

    public Guid Id { get; private set; }
}

/// <summary>
/// Application-layer CRUD port. The generic constraint guarantees that every
/// entity supplied to the application has a Guid Id.
/// </summary>
public interface IGenericRepository<TEntity>
    where TEntity : EntityBase
{
    Task<TEntity> AddAsync(TEntity entity, CancellationToken cancellationToken = default);

    Task<TEntity?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<TEntity>> ListAsync(CancellationToken cancellationToken = default);

    Task<TEntity> UpdateAsync(TEntity entity, CancellationToken cancellationToken = default);

    Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default);
}

/// <summary>
/// Application-layer coordination port. A new EntityBase-derived type gets
/// the same repository CRUD surface through Repository<TEntity>().
/// </summary>
public interface IUnitOfWork : IAsyncDisposable
{
    IGenericRepository<TEntity> Repository<TEntity>()
        where TEntity : EntityBase;

    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}

/// <summary>
/// Dependency-free infrastructure-shaped implementation for contract tests.
/// A production adapter would replace the dictionary with a database context.
/// </summary>
public sealed class InMemoryGenericRepository<TEntity> : IGenericRepository<TEntity>
    where TEntity : EntityBase
{
    private readonly Dictionary<Guid, TEntity> _entities = new();

    public Task<TEntity> AddAsync(TEntity entity, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        ArgumentNullException.ThrowIfNull(entity);
        if (!_entities.TryAdd(entity.Id, entity))
        {
            throw new InvalidOperationException($"Entity already exists: {entity.Id}");
        }

        return Task.FromResult(entity);
    }

    public Task<TEntity?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        _entities.TryGetValue(id, out var entity);
        return Task.FromResult(entity);
    }

    public Task<IReadOnlyList<TEntity>> ListAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        IReadOnlyList<TEntity> result = _entities.Values.ToList().AsReadOnly();
        return Task.FromResult(result);
    }

    public Task<TEntity> UpdateAsync(TEntity entity, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        ArgumentNullException.ThrowIfNull(entity);
        if (!_entities.ContainsKey(entity.Id))
        {
            throw new KeyNotFoundException($"Entity does not exist: {entity.Id}");
        }

        _entities[entity.Id] = entity;
        return Task.FromResult(entity);
    }

    public Task<bool> DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        return Task.FromResult(_entities.Remove(id));
    }
}

/// <summary>
/// Dependency-free Unit of Work coordinator for contract tests. The in-memory
/// repositories mutate immediately; SaveChangesAsync is a coordination boundary,
/// not evidence of database transactionality.
/// </summary>
public sealed class InMemoryUnitOfWork : IUnitOfWork
{
    private readonly Dictionary<Type, object> _repositories = new();
    private bool _disposed;

    public IGenericRepository<TEntity> Repository<TEntity>()
        where TEntity : EntityBase
    {
        ThrowIfDisposed();
        if (_repositories.TryGetValue(typeof(TEntity), out var existing))
        {
            return (IGenericRepository<TEntity>)existing;
        }

        var created = new InMemoryGenericRepository<TEntity>();
        _repositories.Add(typeof(TEntity), created);
        return created;
    }

    public Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        ThrowIfDisposed();
        cancellationToken.ThrowIfCancellationRequested();
        return Task.FromResult(0);
    }

    public ValueTask DisposeAsync()
    {
        _disposed = true;
        _repositories.Clear();
        return ValueTask.CompletedTask;
    }

    private void ThrowIfDisposed()
    {
        if (_disposed)
        {
            throw new ObjectDisposedException(nameof(InMemoryUnitOfWork));
        }
    }
}
