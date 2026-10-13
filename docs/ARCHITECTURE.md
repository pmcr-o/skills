# PMCR-O Architecture

PMCR-O is a marketplace-centered agent system. The marketplace is the canonical top-level SYSTEM; plugins are distributable subsystems; agents are controllers; skills are reusable capabilities; transports carry calls; Trails, Cycles, Frames, and Evidence record operation.

## Canonical hierarchy

```text
MARKETPLACE
  -> PLUGINS
    -> SYSTEMS / PRODUCTS
      -> AGENTS
      -> SKILLS
      -> COMMANDS
      -> HOOKS
      -> WORKFLOWS
      -> MCP / A2A / OpenAPI / gRPC / local transports
```

The canonical repository control plane lives under `.pmcro/`. Provider-native trees such as `.claude/`, `.claude-plugin/`, Codex surfaces, Ollama bindings, Microsoft Agent Framework adapters, MCP manifests, and A2A cards are projections. A projection MUST NOT become a second source of truth.

## Agent cognition

Every PMCR-O agent keeps one durable identity while traversing exactly one cognitive Cycle:

`ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`

Role and phase are orthogonal. `pmcro-planner` is a role agent, not the PLAN phase. `pmcro-checker` is a role agent, not the CHECK phase.

External capability, tool, host, or transport calls are admitted only during MAKE. CHECK evaluates completed evidence and does not repair. REFLECT emits exactly one unexecuted next-seed intent.

## Capability and authority

`AGENT != MODEL != SKILL != CAPABILITY != TRANSPORT != AUTHORITY`.

A provider, shell, model, network endpoint, or registered transport does not grant execution authority by existing. Generated executable capability follows `CREATE -> CHECK -> REGISTER -> later USE`.

## Marketplace filesystem direction

PMCR-O mirrors proven provider component boundaries rather than renaming them unnecessarily. Canonical component names include `agents/`, `skills/`, `commands/`, `rules/`, `hooks/`, `workflows/`, `evals/`, `scripts/`, `bin/`, settings, and MCP/LSP bindings. PMCR-O adds only system-specific layers such as `protocol/`, `trails/`, `cycles/`, `frames/`, `evidence/`, `models/`, `registry/`, and `projections/`.

## Registry and durable transport

The canonical registry under `.pmcro/registry/` controls Planner admissibility. A resource becomes selectable only after independent CHECK and explicit registration; revocation removes admissibility without deleting provenance. Registry resolution is read-only and never invokes the resolved resource.

Durable messages are transport data, not cognition. A queue may provide at-least-once delivery, deduplication, atomic claims, receipts, leases, retries, and dead-letter handling, but transport MUST NOT grant authority, inject a cognitive phase, or execute a reflected next seed. Cross-agent work references immutable messages and source trails rather than co-editing one shared mutable trail.
## Documentation and conformance

Architecture documentation follows this chain:

`ARCHITECTURE -> ADR -> SPECIFICATION -> SCHEMA -> IMPLEMENTATION -> TEST -> EVIDENCE`

ADRs explain why architectural law exists. Specifications use normative MUST/SHOULD/MAY language. Schemas define machine-readable contracts. Deterministic tests establish conformance. Evidence records observed results.

## Training data

Operational Trail data is not training data by default. Training candidates require explicit opt-in, provenance, sanitization/redaction, an independent checker verdict, and role-specific evaluation. Secrets, credentials, private reasoning, and unapproved user content are excluded. Maker and Checker datasets and evaluation evidence remain distinct to strengthen checker independence.

## Verified capability planning and evolution

The Orchestrator manages admitted high-level goals and selects from cataloged agent identities. The Planner builds the minimum sufficient capability graph from registered, checked agents and skills. Physical host availability is not planning authority. A missing capability is an explicit gap, not an invitation to invent functionality.

Maker may resolve an admitted gap through the registered Skill Creator, producing a `generated-unchecked` skill or agent candidate. CHECK may verify the candidate, registration may make it available, and only a later Cycle may select it. REFLECT never loops directly back into MAKE; it emits exactly one unexecuted next seed that starts a fresh Cycle at ORCHESTRATE.

Agent evolution objectives are CREATE, OPTIMIZE, ENHANCE, REFINE, and SPECIALIZE. Prefer instruction/context/skill/capability/policy/eval refinement before model adaptation or training.

## Specialization

Specialized product agents MAY add constraints, schemas, validation, and narrower capability selections. Specialization MUST NOT weaken phase order, independent checking, provenance, grant boundaries, secret handling, or next-seed non-execution.
