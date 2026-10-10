# Sample prompts

Use these to start the skill creator. Keep them short and concrete.

## Prompt 1 — bootstrap a bounded skill

```text
Bootstrap a provider-neutral `inventory-crud` skill in a local workspace. Inspect the existing marketplace first, run dry-run, and report the planned agents/, scripts/, references/, assets/, tests/, and sample-prompts.md files.
```

## Prompt 2 — use the requested Windows target

```text
Create the staged skill workspace for `A:\agent-skills` if that drive is available. If it is not mapped, stop and report the required handoff path instead of writing somewhere else.
```

## Prompt 3 — validate before promotion

```text
Validate the generated skill from a fresh checker context. Report exact paths, hashes, PASS/LOOP/HALT, and one unexecuted next seed; do not publish.
```
