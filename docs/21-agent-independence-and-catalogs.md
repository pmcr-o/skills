# Agent independence, reasoning checks, and catalogs

When a repository contains a reasoning step followed by a check, it is using a
domain projection of the PMCR-O role graph. The names may be `reasoner`,
`reviewer`, `evaluator`, `critic`, `validator`, or `checker`; the contract
determines the meaning.

## Three meanings of independent

“Every agent is independent” is useful when it means every agent is a
first-class, addressable capability. It must not be confused with checker
independence.

| Property | Required for every agent surface | Required for an independent checker |
| --- | --- | --- |
| Addressable identity | Stable id, version, entrypoint, inputs, outputs, scope | Yes |
| Bounded authority | Own grant, limits, dependencies, and context boundary | Yes |
| Separate execution | Can be invoked as its own bounded capability | Yes; fresh checker context is stronger |
| Maker isolation | May consume a maker result according to its contract | Read-only maker artifact; no maker edits |
| Verdict authority | May return its declared result | Only checker owns `PASS`, `LOOP`, or `HALT` |
| Self-certification | Not implied by having an agent file | Explicitly denied |

The repository records this distinction as:

- `independentSurface: true`: the capability has its own typed agent surface
  and can be addressed or tested independently.
- `independentChecker: true`: the capability has the stronger checker contract:
  fresh context, bounded stop cap, read-only maker output, and verdict-only
  authority.

Therefore a planner, maker, catalog, or reflector can be independently
addressable while still having `independentChecker: false`.

## Reasoning plus check mapping

| Repository pattern | PMCR-O projection | Acceptance boundary |
| --- | --- | --- |
| Reasoning/proposal agent | `PLAN` or `MAKE` | Emits a proposal, artifact, or evidence claim; no verdict |
| Check/review agent | `CHECK` | Re-reads the contract and reruns declared proofs |
| Reflection/learning agent | `REFLECT` | Records the earned constraint and one unexecuted next seed |
| Catalog/router agent | `ORCHESTRATE` resource discovery | Lists or routes validated capabilities; does not promote them |

If one agent generates a result and immediately checks its own result in the
same context, that is a self-check or internal quality step. It is useful, but
it is not the independent checker required for a PMCR-O `PASS`.

## Verified W: repository mapping

Desktop Commander performed a read-only inspection on `PMCRO_Company` on
2026-10-09. These are repository observations, not claims about private
implementations elsewhere:

| Observed source | Verified meaning | PMCR-O mapping |
| --- | --- | --- |
| `W:\pmcro-skills\.agents\agents\planner\agent.md`, `maker\agent.md`, `checker\agent.md`, `reflector\agent.md` | Phase agents are addressable, but the files explicitly separate phase work from host/seat startup; checker is not a seat. | `PLAN`, `MAKE`, `CHECK`, `REFLECT` are typed phase surfaces. |
| `W:\pmcro-skills\plugins\pmcro\skills\make\SKILL.md` and `check\SKILL.md` | Make changes only named files and does not write the verdict; check reads plan/make and validates them. | Maker/checker authority is separated by contract. |
| `W:\pmcro-skills\plugins\pmcro\skills\reflect\SKILL.md` and `.agents\agents\cdo\agent.md` | Reflect copies a completed verdict into an earned constraint/next seed; trail quality does not issue a checker verdict. | `REFLECT` learns; it does not promote. |
| `W:\ProjectName\GOVERNANCE.md` and `ProjectName.slnx` | Planner, Maker, Checker, and Reflector have separate MAF identities/projects under a shared policy kernel. | MAF Native is a runtime adapter for the role graph. |
| `W:\ProjectName\src\Services\ProjectName.OrchestratorService\Cycle\PmcroCycle.cs` | The checker runs in a new workflow/session and receives serialized intent/planner/maker data; it parses the verdict separately. The same device/account is not a distinct security principal. | Fresh context supports checker independence; identity still needs a real deployment boundary. |
| `W:\ProjectName\src\Services\ProjectName.OrchestratorService\Cascade\PmcroLoop.cs` | The orchestrator owns the parent goal, cycle/depth caps, registry lookup, and missing-skill child goal. | Catalog/registry discovery belongs upstream of planning and cannot promote by itself. |
| `W:\ProjectName\docs\platform\INDEPENDENT_REVIEW.txt` and `ROADMAP.md` | Review records its scope and claim limits; current text cycles do not prove MCP execution, autonomous terminal work, or production deployment. | Evidence tier stays explicit: simulation, deterministic proof, runtime proof, promotion. |

The inspection also confirmed a practical convention: a repository can expose
many independently addressable phase agents while reserving independent
checker authority for one bounded surface. That is the convention this
repository now validates with `independentSurface` and `independentChecker`.

## Catalog agents

A catalog may itself be an agent. Its safe contract is read-only progressive disclosure:

1. receive a capability query and principal/scope;
2. return metadata, exact package/ref identifiers, dependencies, and evidence
   status;
3. reveal a requested contract or prompt packet;
4. hand the selected resource to the orchestrator for planning.

The catalog does not certify, promote, or turn a listing into authority,
execution, or trust. `thought-transfer.catalog-mcp-server` is intentionally
`independentChecker: false` even though it has its own independent surface.
The orchestrator still requires a checker before promotion.

## Production-shaped composition

The general production pattern is a separation of router/catalog, planner or
reasoner, bounded worker, evaluator, and policy/harness boundary. This
repository expresses that pattern declaratively; it does not claim knowledge
of any private implementation used by a particular LLM company.

The important invariant is the handoff, not the brand name:

```text
catalog -> orchestrator -> reasoner/maker -> fresh checker -> reflector
```

Every edge carries a typed envelope, scope, grant, evidence, and next owner.
MAF WorkflowBuilder, CodeAct-style execution, Harness policy, and MCP tools
are runtime adapters around this graph; they do not decide whether a result is
an independent checker verdict.

See also:

- `plugins/pmcro/references/agent-independence-and-catalogs.md`
- `docs/13-agent-surface-api-and-scope.md`
- `skills/pmcro-agent-surface/references/agent-surface-contract.md`
