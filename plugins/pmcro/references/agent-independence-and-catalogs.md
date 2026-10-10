# Agent independence and catalogs

Use this reference when mapping a repository’s reasoning/check pattern into
PMCR-O.

Every agent is independently addressable through an id, entrypoint, typed
inputs/outputs, scope, grant, and context boundary. That is recorded as
`independentSurface: true`.

An independent checker is a stricter role. It must use a fresh boundary, stop
after its cap, read the maker artifact without editing it, rerun acceptance
proofs, and own the `PASS`/`LOOP`/`HALT` verdict. That is recorded separately as
`independentChecker: true`.

A catalog agent may list and progressively disclose capabilities, refs,
dependencies, and prompt packets. It remains read-only and cannot certify or
promote the resources it lists. The orchestrator consumes its result as a
validated resource candidate, not as authority.

The catalog therefore declares `independentChecker: false`; being independently
addressable does not grant verdict authority.

Verified W: evidence includes a dedicated checker phase agent and separate
`ProjectName.PlannerService`, `ProjectName.MakerService`,
`ProjectName.CheckerService`, and `ProjectName.ReflectorService` projects. The
ProjectName cycle creates a new checker workflow/session with serialized
task/artifact data, while its own review record correctly limits that to a
fresh checker call rather than a distinct security principal. The orchestrator
cascade separately owns cycle/depth caps and registry/missing-skill routing.

The detailed mapping is in `docs/21-agent-independence-and-catalogs.md`.
