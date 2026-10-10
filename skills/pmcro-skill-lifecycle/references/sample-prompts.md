# Sample prompts

Use these to start the skill lifecycle gate.

## Prompt 1 — create a skill request

```text
Emit a skill.create.request for a bounded dotnet-console-output skill. Include required folders/files, the agent manifest, sample-prompt reference, message contract, validated resources, and simulate mode.
```

## Prompt 2 — reconcile a marketplace skill

```text
Run the skill-creator gate for an existing skill repository. Inspect first, preserve unknown files, produce a dry-run request, and do not register the marketplace entry before independent checking.
```

## Prompt 3 — specialize a generic child

```text
Create a sample-child specialization from the generic skill template. Add only domain references, scripts, assets, tests, and prompts; inherit the parent grant and leave promotion unexecuted.
```
