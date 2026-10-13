# A:\marketplace reconciliation map

This artifact is generated from read-only inspection of `A:\marketplace` and comparison against the checked C: PMCR-O contracts. It does not authorize mutation of A:.

Source catalog schema: `agent-marketplace-project/v3`  
Canonical agents observed: **25**  
Legacy marketplaces observed: **6**

## Classification law

`ADOPT` = aligned pattern worth importing subject to normal CHECK. `MERGE` = overlaps current canonical work and needs reconciliation. `SUPERSEDE` = conflicts with checked law. `REFERENCE` = provenance/evidence only. `DEFER` = potentially useful but insufficiently reconciled.

## Agent projects

| Agent | Role | Declared skills | Observed SKILL.md | Classification |
| --- | --- | ---: | ---: | --- |
| `pmcro-agent` | global-orchestrator | 17 | 136 | **MERGE** |
| `csuite-agent` | domain-meta-orchestrator | 15 | 120 | **ADOPT** |
| `agent-skills-template` | template-orchestrator | 6 | 48 | **ADOPT** |
| `dotagents-agent` | domain-orchestrator | 6 | 48 | **MERGE** |
| `dotnet-agent` | domain-orchestrator | 113 | 1014 | **ADOPT** |
| `github-agent` | domain-orchestrator | 10 | 80 | **ADOPT** |
| `docker-agent` | domain-orchestrator | 2 | 16 | **ADOPT** |
| `powershell-agent` | domain-orchestrator | 1 | 8 | **ADOPT** |
| `filesystem-agent` | domain-orchestrator | 2 | 16 | **ADOPT** |
| `governance-agent` | domain-orchestrator | 1 | 10 | **MERGE** |
| `desktop-commander-agent` | domain-orchestrator | 1 | 8 | **MERGE** |
| `skill-creator-agent` | domain-orchestrator | 4 | 32 | **MERGE** |
| `reasoning-agent` | domain-orchestrator | 10 | 82 | **ADOPT** |
| `maf-agent` | domain-orchestrator | 3 | 32 | **MERGE** |
| `social-media-agent` | domain-orchestrator | 3 | 24 | **ADOPT** |
| `git-agent` | domain-orchestrator | 2 | 16 | **ADOPT** |
| `python-agent` | domain-orchestrator | 2 | 16 | **ADOPT** |
| `aspire-agent` | domain-orchestrator | 3 | 24 | **ADOPT** |
| `computer-use-agent` | domain-orchestrator | 2 | 20 | **ADOPT** |
| `model-gateway-agent` | domain-orchestrator | 2 | 16 | **ADOPT** |
| `eval-agent` | domain-orchestrator | 3 | 24 | **ADOPT** |
| `federation-agent` | domain-orchestrator | 3 | 24 | **ADOPT** |
| `confidentiality-agent` | domain-orchestrator | 3 | 24 | **ADOPT** |
| `resource-registry-agent` | domain-orchestrator | 4 | 32 | **ADOPT** |
| `economics-agent` | domain-orchestrator | 4 | 32 | **ADOPT** |

## Legacy marketplace trees

- `dotagents-marketplace` — **REFERENCE**: migration-evidence.
- `dotnet-skills-marketplace` — **REFERENCE**: migration-evidence.
- `filesystem-marketplace` — **REFERENCE**: migration-evidence.
- `github-marketplace` — **REFERENCE**: migration-evidence.
- `powershell-marketplace` — **REFERENCE**: migration-evidence.
- `skill-creator-marketplace` — **REFERENCE**: migration-evidence.

## Architectural concepts

- **ADOPT** `pmcro-canonical-authority` — A:/marketplace README/catalog declare .pmcro canonical; matches checked C: law.
- **ADOPT** `provider-projections` — A: host -> .agents -> .pmcro projection chain matches provider-projection law.
- **MERGE** `generated-domain-agent-projects` — A: eng/src and refresh/build tooling provide a mature generator model to reconcile with C: projection compiler.
- **MERGE** `agent-registry-and-filesystem-queues` — A: agent-registry.json binds local paths and filesystem-spool-v1 queues; richer than current C: registry.
- **ADOPT** `pinned-upstream-source` — A: eng/upstream uses pinned vendor source plus lock digest; compatible with provenance law.
- **ADOPT** `independent-marketplace-validation` — A: eng/validate-agent-repos.py is explicitly independent whole-marketplace validation.
- **SUPERSEDE** `mandatory-all-skill-folders` — A: eng/README requires scripts/references/assets/tests for every owned skill; current C: law requires only SKILL.md + agents/ and optional progressive layers.
- **SUPERSEDE** `automatic-post-reflect-cycle` — A: agent contracts automatically admit REFLECT next seed; checked C: next-seed law keeps it unexecuted until a fresh admitted Cycle.
- **DEFER** `recursive-phase-cycles` — A: contracts allow recursive lifecycle inside every bounded phase; current law only clearly admits explicit child delegation as a child Cycle.
- **DEFER** `i-context-accountability-frame` — A: pmcro.i-context/v1 appears useful but has no checked equivalent in current C: contracts yet.
- **MERGE** `cross-agent-local-trails` — A: each I owns a local trail and cross-I handoffs reference source trails; reconcile with current trail/evidence graph.
- **ADOPT** `transport-model-not-authority` — A: explicitly states transport/model identity never grants authority; matches checked C: law.
- **ADOPT** `maker-no-self-certification` — A: Maker output remains evidence until independent CHECK; matches current C: law.
- **REFERENCE** `eng-history` — A: eng/history is declared superseded provenance and must not drive new builds.

## Mutation boundary

No A: file, repository state, registry entry, queue, generated project, or trail is changed by this reconciliation map. Future migration must consume this map as source evidence and run CREATE/CHECK/REGISTER in the canonical workspace before later use.
