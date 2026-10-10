# Typed agent surfaces, scopes, and MAF Native adapters

This repository treats Everything-as-Agent as a contract pattern: a service,
plugin, workflow, MCP endpoint, marketplace skill, or ordinary tool can expose
the same PMCR-O surface without pretending its implementation is an LLM.

## Scope model

| Layer | Example | Owns | Inheritance |
|---|---|---|---|
| Global | `pmcro.global-orchestrator` | shared templates and catalog defaults | none |
| Personal | `pmcro.personal-orchestrator` | one principal's preferences/grants | explicit global, non-widening |
| Project | `projectname.orchestration-service` | project service and layout | explicit global, non-widening |
| Run | activation envelope/trail cycle | ephemeral state and evidence | explicit project/personal |

The account and project screenshots supplied with this trail motivate the
separation: host-specific `.claude` files and global account state are
projections with different lifetimes. The generic `.agents` and `.pmcro`
directories keep the contract portable across ChatGPT, Claude, Gemini, local
Ollama, and MAF Native. A folder or account does not silently grant authority.

## API simulation

The local contract models routes such as:

```text
GET  /v1/scopes/global/agents/{agentId}
GET  /v1/users/{userId}/agents/{agentId}
GET  /v1/projects/{projectId}/agents/{agentId}
POST /v1/orchestrator-runs
```

The response carries `simulation: true`, `verified: false`, and
`evidenceTier: pattern-valid` until an independent checker has direct runtime
evidence. `POST /v1/orchestrator-runs` predicts the strict PMCR-O phases; it
does not execute them.

Run the demonstration:

```bash
python3 skills/pmcro-agent-surface/scripts/validate_surface.py --repo .
python3 skills/pmcro-agent-surface/scripts/simulate_agent_api.py \
  --repo . --request skills/pmcro-agent-surface/assets/agent-surface-request.json
```

## MAF Native alignment

`maf-workflows` owns role executors and JSON checkpoints; `maf-mcp-tools` owns
allowlisted MCP connections; `filesystem` owns relative file discovery and
CRUD according to its own grant. The PMCR-O plugin composes those existing
capabilities rather than inventing a second runtime. In a real .NET repository,
the MAF package versions and the declared `ProjectName.OrchestrationService`
entrypoint must be checked before execution.

## Evidence boundary

The checked repository proves the contract, route shape, scope inheritance, and
local simulation. It does not prove that a .NET service, MAF workflow, MCP
server, cloud provider, or user account was invoked. That future result belongs
to a new bounded seed with its own grant and checker.
