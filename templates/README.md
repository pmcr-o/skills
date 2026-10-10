# Template examples and contracts

The files in this directory are reusable declarative templates, not complete
applications.

| Template | Purpose | Inputs | Expected output | Evidence and limits |
| --- | --- | --- | --- | --- |
| `skill-manifest.json` | Define a generated skill's folders, contract, caps, and example-documentation rule | Skill identity and contract fields | Valid skill manifest | Structural pattern only |
| `SKILL.md.tmpl` | Render readable skill instructions | Display name, purpose, limits | Progressive-disclosure instructions | Does not grant runtime authority |
| `agent-surface.json` | Declare scoped agent identity and grants | Component, scope, dependencies | Typed agent surface | Simulation until checked |
| `crud-envelope.json` | Request bounded CRUD over a resource | Resource, operation, scope, version | `CrudRequest` | Does not mutate a resource by itself |
| `skill-output-envelope.json` | Normalize skill handoffs | Input, output, evidence, next action | `SkillOutput` | `verified=false` until direct evidence |
| `sample-prompts.md.tmpl` | Give a skill short copy/paste starters | Skill purpose and bounded examples | Prompt cards for a skill UI | Does not grant authority or execute a task |
| `product-repo/` | Generate a friend-run, provider-neutral agent product repository | Product intent, principal, adapters, and finite grant | Manifest, agent surfaces, generic trail, validators | Routine autonomy only inside the grant; checker required |

Every template consumer must document its concrete examples in the owning
skill's `assets/README.md` or a linked document. Every installable skill also
publishes short invocation examples in `references/sample-prompts.md`.
