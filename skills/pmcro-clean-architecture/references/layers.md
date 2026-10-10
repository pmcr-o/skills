# Clean Architecture layer contract

| Layer | Baseline artifact | Rule |
| --- | --- | --- |
| Domain | `EntityBase`, entities, value objects | No persistence or provider dependency |
| Application | `IGenericRepository<TEntity>`, `IUnitOfWork`, use cases | Depends on Domain; owns ports and policies |
| Infrastructure | Generic repository and Unit of Work adapters | Implements ports; owns database/provider details |
| API/worker | Endpoints, handlers, agent surface | Translates transport into application requests |
| Tests | Domain/application/integration checks | Proves the declared contract at the appropriate evidence tier |

The generic repository gives a new `EntityBase`-derived type common CRUD
operations. It does not generate aggregate-specific queries, authorization,
transaction isolation, concurrency tokens, audit, outbox delivery, or domain
invariants. Those are named acceptance requirements for the application.

The builder may emit a file plan or a staged scaffold. It must preserve the
same PMCR-O output envelope across simulation, replay, and execution modes.
