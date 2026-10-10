# MAF chain and default output

Every capability starts with the same declarative interface:

`resource -> operation -> grant -> typed output envelope -> checker -> trail`

MAF Native can wrap each operation as an executor and connect executors through
the envelope. The default profiles are `json` for machines, `dotnet-console`
for a human-readable simulation, and `trail` for append-only evidence. A
profile changes presentation, not authority or evidence.

Generic CRUD operations use these safe meanings:

| Operation | Default result | Runtime requirement |
|---|---|---|
| create | staged new version | declared write grant |
| read | progressive projection | read grant |
| update | new version linked to predecessor | write + concurrency check |
| delete | revoke/tombstone | explicit deletion policy and checker |

The workflow may simulate all four operations, but a simulation only proves the
envelope and route. A real MAF executor must record its checkpoint, operation
id, resource version, authorization decision, output hash, and checker result.
