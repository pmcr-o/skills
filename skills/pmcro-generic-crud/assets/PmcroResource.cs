using System;
using System.Threading;
using System.Threading.Tasks;

namespace ThoughtTransfer.Pmcro;

public enum PmcroLifecycle
{
    Candidate,
    Staged,
    Active,
    Deprecated,
    Revoked,
}

/// <summary>
/// Domain-neutral identity and lifecycle contract for a PMCR-O resource.
/// Persistence, authorization, auditing, and serialization remain application concerns.
/// </summary>
public abstract record PmcroResource<TId, TVersion>
    where TId : notnull
    where TVersion : notnull
{
    public required TId Id { get; init; }
    public required string Scope { get; init; }
    public required TVersion Version { get; init; }
    public TVersion? PreviousVersion { get; init; }
    public PmcroLifecycle Lifecycle { get; init; } = PmcroLifecycle.Candidate;
    public required string ContentHash { get; init; }
    public DateTimeOffset UpdatedAt { get; init; } = DateTimeOffset.UtcNow;

    public abstract string Kind { get; }
}

public sealed record PmcroCrudRequest<TId, TVersion>(
    string RequestId,
    string TraceId,
    TId ResourceId,
    string Scope,
    string Operation,
    TVersion? ExpectedVersion,
    string OutputProfile);

public sealed record PmcroCrudResult<TResource>(
    string OperationId,
    TResource? Resource,
    string Status,
    bool Simulation,
    bool Verified,
    string EvidenceTier);

public interface IPmcroCrudStore<TResource, TId, TVersion>
    where TResource : PmcroResource<TId, TVersion>
    where TId : notnull
    where TVersion : notnull
{
    ValueTask<PmcroCrudResult<TResource>> CreateAsync(
        TResource resource, CancellationToken cancellationToken = default);

    ValueTask<PmcroCrudResult<TResource>> ReadAsync(
        TId id, string scope, CancellationToken cancellationToken = default);

    ValueTask<PmcroCrudResult<TResource>> UpdateAsync(
        TResource resource, TVersion expectedVersion, CancellationToken cancellationToken = default);

    ValueTask<PmcroCrudResult<TResource>> RevokeAsync(
        TId id, string scope, TVersion expectedVersion, string reason,
        CancellationToken cancellationToken = default);
}
