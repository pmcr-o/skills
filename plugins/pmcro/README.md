# PMCR-O plugin

This plugin is the federation boundary for the repository's PMCR-O skills. It
does not duplicate every provider-specific implementation. The manifest maps
the local agent-surface projection to versioned marketplace skills and names
the MAF Native adapters that may be activated under a separate grant.

## Contract

```text
intent -> BIP -> typed agent surface -> catalog/federation -> MAF adapter
       -> simulate/replay/execute -> independent check -> trail product
       -> staged skill/template/eval/catalog child
```

The same envelope is used for a real service, a plugin, a workflow, an MCP
endpoint, or a marketplace skill. `ProjectName.OrchestrationService` is a
project-scoped service surface; it is not automatically global merely because
it can orchestrate other components.

The plugin has five conceptual core skills:

| Skill | Responsibility |
|---|---|
| `pmcro-bip` | compile intent into observable behavior |
| `pmcro-agent-surface` | expose typed identity, modes, grants, and evidence |
| `pmcro-marketplace` | discover, stage, validate, and compose artifacts |
| `pmcro-github-marketplace` | federate pinned repositories progressively |
| `pmcro-trail-product` | turn checked trails into reusable products |

See `references/maf-native-filesystem.md` for why filesystem discovery is an
adapter rather than an authority grant. See `references/progressive-disclosure.md`
for the token-bounded catalog views.

The generic starting point is `pmcro-generic-crud`: its resource contract can
be projected into a .NET abstract generic base model, a JSON catalog record, or
a trail/memory entry without changing the PMCR-O handoff envelope.
