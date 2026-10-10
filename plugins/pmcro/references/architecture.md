# PMCR-O architecture

The canonical design is generic and template-driven. Provider folders are
projections, not independent authorities.

```text
global template/catalog
        -> personal projection
        -> project projection
        -> run envelope and trail
        -> checked trail product
        -> staged marketplace child
```

The repository uses `.agents/` for declarative agent surfaces and `.pmcro/` for
protocol, trails, and evidence. A provider may project the same contract into
`.claude/`, `.codex/`, `.gemini/`, or another host-specific directory. The
projection must retain `templateRef`, `extends`, scope, grant, limits, and
trail references.

The attached project-layout screenshot shows a project `.claude/` containing
`CLAUDE.md`, path-scoped rules, skills, commands, output styles, agents,
workflows, and agent memory. The account-layout screenshot shows global
`.claude.json`/`.claude/` state with MCP configuration, project memory, and
agent-memory. These are useful host projections; they do not replace the
generic `.agents`/`.pmcro` source of truth.

No folder name creates authority. Authority is a versioned grant in the
activation envelope and is checked at the boundary.

When the same idea crosses .NET, JSON, a skill, MAF, MCP, or another domain,
use semantic concept mapping: preserve the invariant in the canonical envelope
and declare the domain adapter and evidence tier. See
`generic-concept-mapping.md` and `docs/19-generic-concept-mapping.md`.
