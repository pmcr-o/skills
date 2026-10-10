# Sample prompts

Use these to start the messages-protocol skill. Keep them short and concrete.

## Prompt 1 — validate frames

```text
Validate this JSONL trail for role-owned message kinds, contiguous sequence, parent links, and hash-chain integrity. Report the first failing frame.
```

## Prompt 2 — create a handoff

```text
Create a planner-to-maker handoff with scope, validated resources, acceptance evidence, and one bounded next action. Do not execute it.
```

## Prompt 3 — reject self-approval

```text
Check whether this maker frame attempts to issue its own PASS verdict. If it does, return LOOP or HALT with the violated protocol rule.
```
