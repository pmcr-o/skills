# Plugin skill map

The installable implementations remain in the repository `skills/` catalog so
the existing validator and marketplace can find them. This folder records the
plugin's conceptual skill boundary; the canonical paths and external packages
are in `../plugin.json`.

| Plugin skill | Canonical source | Role |
|---|---|---|
| `pmcro-bip` | executor skill package | intent/behavior compiler |
| `pmcro-agent-surface` | `skills/pmcro-agent-surface/` | local typed surface and API simulation |
| `pmcro-marketplace` | executor skill package | recursive staged marketplace |
| `pmcro-github-marketplace` | executor skill package | pinned repository federation |
| `pmcro-trail-product` | executor skill package | progressive trail product |
| `pmcro-memory-governance` | `skills/pmcro-memory-governance/` | scoped, checked memory promotion |

An external package is a dependency reference, not a claim that its runtime was
executed in this repository. The checker must resolve and test it before a
candidate is promoted.
