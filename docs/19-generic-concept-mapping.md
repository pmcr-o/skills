# Generic concept mapping across domains

In this repository, “generic” means **semantically reusable**, not “copy the
same source code everywhere.” A concept starts as a contract, then each domain
projects that contract into its own types, files, APIs, tools, or runtime. The
projection is valid only when its preserved invariants and its losses are
explicit.

## The mapping pattern

| Concept | Canonical PMCR-O meaning | .NET/Clean Architecture projection | Skill/JSON projection | MAF/MCP/runtime projection |
| --- | --- | --- | --- | --- |
| Identity | Stable identifier for a resource or actor | `EntityBase<Guid>.Id` | `agent.id`, resource `id` | executor/agent identity in a workflow envelope |
| Scope and grant | Where the capability may act and what it may touch | application boundary and repository dependency | `scope`, `target_root`, `grant` | Harness sandbox, allowlist, budget, and cancellation |
| Operation | A typed action with inputs and evidence | `IGenericRepository<TEntity>` CRUD port | `input`, `output`, `accept`, `deny` | CodeAct-style bounded action or an allowlisted MCP tool |
| Phase and handoff | Meaning of the current step and the next owner | application/infrastructure boundary | `phase`, `checker_handoff`, `next_seed` | MAF executor edge and checkpoint; PMCR-O still owns phase meaning |
| Independent check | A fresh evaluation that cannot edit or certify itself | test/checker project or process | `independentChecker: true`, verdict evidence | fresh checker context, separate from the maker executor |
| Artifact projection | A domain-shaped representation of the same checked result | C# source, interface, adapter, or DTO | manifest, `SKILL.md`, JSONL trail | workflow output, MCP result, console rendering |

The shared meaning is the contract column. The other columns are domain adapters.
For example, `EntityBase<Guid>` and `PmcroResource<TId,TVersion>` both express a
stable identity, but they are not interchangeable domain models: one belongs to
an application entity and the other to a versioned PMCR-O resource.

## How to create a mapping

1. **Name the concept and invariant.** State what must remain true, such as
   “every entity has a stable identity” or “a checker cannot edit maker output.”
2. **Choose the canonical envelope.** Record identity, scope, grant, phase,
   input, output, acceptance, denial, evidence, and next owner in the PMCR-O
   contract.
3. **Write one adapter per domain.** Map the invariant to the domain’s native
   type or operation. Do not force a .NET class, a JSON record, an MCP tool, and
   a workflow executor to share a false common implementation.
4. **Declare loss and assumptions.** A mapping that cannot preserve a field
   must say `not_supported`, `simulation_only`, or `requires_external_ref`.
   Missing source identity, license, version, or runtime evidence blocks
   federation; it is not silently guessed.
5. **Simulate the projection.** Render the domain-shaped output and verify its
   envelope, required folders, limits, and evidence references locally.
6. **Check independently.** An independent checker reruns the acceptance
   commands and decides `PASS`, `LOOP`, or `HALT`. Only a checked result may
   become a reusable template or marketplace product.

## Mapping levels

These levels must not be conflated:

- **Semantic mapping:** two representations preserve the same declared concept
  or invariant.
- **Structural mapping:** the target has the required fields, folders, or
  interfaces.
- **Runtime mapping:** a real host can execute the target with the declared
  grants, tools, and lifecycle.
- **Evidence mapping:** the target has independently checkable proof for the
  claim being made.

A structurally similar `MCP` tool is not therefore trusted, a C# file is not
therefore compiled, and a simulated MAF graph is not therefore a running
workflow. The output envelope must retain `simulation=true` and
`verified=false` until the corresponding evidence exists.

## Current projections

The generic CRUD example demonstrates the pattern without claiming universal
interchangeability:

- `EntityBase` supplies application identity; `IGenericRepository<TEntity>`
  supplies a constrained CRUD port; `IUnitOfWork` supplies a coordination and
  save boundary. Therefore every new `EntityBase`-derived type can use the
  existing Add/Get/List/Update/Delete operations without another per-entity
  CRUD repository implementation.
- `PmcroResource<TId,TVersion>` supplies versioned marketplace/control-plane
  identity and provenance. It is a separate model with related concepts.
- The skill contract maps those concepts into input/output/accept/deny records,
  asset documentation, and a checker handoff.
- The runtime reference maps the same handoff into MAF WorkflowBuilder,
  CodeAct-style bounded execution, Harness policy boundaries, and MCP typed
  capabilities.

The generic base gives a new entity a reusable CRUD surface; it does not invent
domain queries, aggregate invariants, transaction isolation, authorization,
concurrency, audit, or outbox behavior. Those remain explicit adapters and
acceptance criteria. When one of those additions is itself CRUD-shaped, the
minimal representation is another typed CRUD port or adapter that composes the
existing contract; only genuinely different behavior requires a new contract.

## CRUD as the universal lifecycle

The same contract can describe the lifecycle of almost any skill, agent,
artifact, memory record, marketplace entry, or trail:

| Lifecycle operation | Skill/agent meaning | Default safety rule |
| --- | --- | --- |
| Create | Stage a new candidate, version, or capability | Create under an explicit scope; do not publish automatically |
| Read | Disclose the requested projection or prompt surface | Progressive disclosure; reveal only the authorized view |
| Update | Produce a new version linked to its predecessor | Check expected version; never silently overwrite |
| Delete | Revoke, tombstone, archive, or request retention deletion | Reversible by default; physical erasure needs policy and a checker |

So “everything follows CRUD” is a useful lifecycle lens. It does not mean that
every domain behavior is merely CRUD. `approve`, `compile`, `send`, `calculate`,
and `check` are typed domain operations with their own inputs, side effects,
and evidence; their results can create or update a governed resource state.
Keeping that distinction lets one CRUD contract organize many domains without
erasing the meaning of their specialized actions.

## Promotion rule

The forward flow may use a checked mapping to generate a project, plugin, skill,
or marketplace entry. The backward flow may extract a redacted, reusable
constraint from its trail. In both directions, the trail retains the source
reference, adapter identity, simulation/verification status, checker evidence,
and unexecuted next seed. A generic concept is therefore a bridge between
domains—not permission to erase their differences.

See also:

- `plugins/pmcro/references/generic-concept-mapping.md`
- `docs/17-clean-architecture-generic-repository.md`
- `skills/pmcro-clean-architecture/references/runtime-mapping.md`
