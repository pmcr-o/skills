# PMCR-O dependency map

```text
pmcro-orchestrator
  -> pmcro-bip
  -> pmcro-agent-surface
       -> filesystem (layout discovery)
       -> pmcro-messages-protocol (typed handoff)
  -> pmcro-marketplace
       -> create-skill / quality / governance
  -> pmcro-github-marketplace
       -> pmcro-federation
  -> maf-workflows (role graph/checkpoints)
  -> maf-mcp-tools (separate MCP tools)
  -> checker
  -> pmcro-trail-product
```

The arrows are dependency references, not automatic invocation. Each activation
must resolve a version/ref, grant, limits, and acceptance evidence. A missing
resource routes to `ASK`/`LOOP`/`HALT`; it is never invented.
