# Template examples and contracts

The files in this directory are reusable declarative templates, not complete
applications.

| Template | Purpose | Inputs | Expected output | Evidence and limits |
| --- | --- | --- | --- | --- |
| `skill-manifest.json` | Define a generated skill's required core, optional progressive-disclosure layers, contract, caps, and example-documentation rule | Skill identity and contract fields | Valid skill manifest | Structural pattern only |
| `SKILL.md.tmpl` | Render readable skill instructions | Display name, purpose, limits | Progressive-disclosure instructions | Does not grant runtime authority |
| `agent-surface.json` | Declare scoped agent identity and grants | Component, scope, dependencies | Typed agent surface | Simulation until checked |
| `crud-envelope.json` | Request bounded CRUD over a resource | Resource, operation, scope, version | `CrudRequest` | Does not mutate a resource by itself |
| `skill-output-envelope.json` | Normalize skill handoffs | Input, output, evidence, next action | `SkillOutput` | `verified=false` until direct evidence |
| `sample-prompts.md.tmpl` | Give a skill short copy/paste starters when that layer is needed | Skill purpose and bounded examples | Prompt cards for a skill UI | Optional; does not grant authority or execute a task |
| `product-repo/` | Generate a friend-run, provider-neutral agent product repository | Product intent, principal, adapters, and finite grant | Manifest, agent surfaces, generic trail, validators | Routine autonomy only inside the grant; checker required |

The canonical installable-skill core is `SKILL.md` plus `agents/` with at least
one machine-readable PMCR-O agent. `references/`, `assets/`, `scripts/`, and
`tests/` are optional progressive-disclosure layers and must not be created
empty merely for conformity. When a skill contains concrete example assets,
document them in `assets/README.md` or a linked document. When a skill exposes
copy/paste invocation examples, keep them bounded in
`references/sample-prompts.md`.
