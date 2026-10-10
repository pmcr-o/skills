# Sample prompts

Use these to start a `{{display_name}}` session. Keep them short and concrete.
They are copy/paste examples, not additional authority.

## Prompt 1 — create a bounded skill

```text
Create a {{skill_name}} skill for {{purpose}}. Ask only the missing questions, then emit the required folders, agent contract, sample prompts, and validation evidence.
```

## Prompt 2 — inspect before applying

```text
Inspect the existing marketplace for {{skill_name}} in dry-run mode. Report conflicts and the smallest staged change; do not overwrite unknown files.
```

## Prompt 3 — validate the result

```text
Validate the generated {{skill_name}} skill from a fresh checker context. Report PASS, LOOP, or HALT with exact evidence and one unexecuted next seed.
```
