# Cascading orchestration

Scopes and roles are separate dimensions:

| Dimension | Values | Meaning |
|---|---|---|
| scope | global, personal, project, run | where identity/configuration is owned |
| role | orchestrator, planner, maker, checker, reflector, service | what the participant may do |
| mode | inspect, simulate, replay, execute, check | how the capability is activated |

The default inheritance path is `global -> personal -> project -> run`, but a
child must declare an exact parent and a non-widening policy. There is no
implicit cascade from a directory, account, model, or provider.

Competing orchestrators are a finite federation wave. Normalize each candidate
by identity, version, source, grant, dependency refs, output schema, policy,
and evidence. Then use a separate checker to select or route. Do not silently
switch providers, run an unbounded debate, or let a child publish its own
authority.

The PMCR-O phase graph remains strict:

`ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`

The reflector can raise the next seed from `meta` to `meta2` or `meta3`, but
the seed remains unexecuted and the next cycle must re-derive intent.
