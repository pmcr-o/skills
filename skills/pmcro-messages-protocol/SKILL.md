---
name: pmcro-messages-protocol
description: Create and validate append-only PMCR-O message frames for orchestrator, planner, maker, checker, and reflector roles. Use when two sessions need a compact resource-first handoff, when installing or reviewing .pmcro/protocol/messages.md and JSONL frame logs, or when enforcing role-owned kinds, hash chains, bounded loops, independent checking, and unexecuted meta-level next seeds.
---

# PMCR-O Messages Protocol

Use this skill to give multiple agent sessions a shared, replayable control-plane format without copying an entire conversation.

## Operating contract

1. Resolve the target repository and authorized `.pmcro/protocol/` path. Do not assume a Windows drive exists in the current environment.
2. Read [messages.md](references/messages.md) before creating or validating frames.
3. Pass only the preserved seed, derived goal, validated resource references, charter, acceptance evidence, and one unexecuted next seed. Request a package by exact ID only when the receiving session cannot access a declared resource.
4. Keep the public route strict: `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`. The orchestrator routes and caps; it never plans or checks. The planner plans from validated resources; it never executes. The maker reports changes without a verdict. The checker issues the only verdict in a fresh context. The reflector agent waits for that completed checker frame, invokes the marketplace `reflect` skill, records constraints, and emits a messy seed; it does not execute its seed.
5. Validate a JSONL frame log with:

   ```bash
   python3 scripts/validate_frames.py path/to/frames.jsonl
   ```

6. Report the exact files, hashes, commands, and validator results. A maker may claim completion but may not claim `PASS`; only an independent checker can issue `PASS`, `LOOP`, or `HALT`.

## Manual execution and simulation

Treat the skill folder as a filesystem-runnable artifact. Run its scripts directly without a model invocation:

```bash
python3 scripts/validate_frames.py assets/examples/valid.jsonl
python3 scripts/validate_frames.py assets/examples/invalid.jsonl  # expected exit 1
```

Inspect `references/messages.md`, the JSONL fixtures, and any generated frame log as ordinary files. A passing simulation proves only that the local contract and validator agree; it is not a live checker verdict. A separate checker session must rerun the script against the handoff before issuing `PASS`.

## Frame rules

- Append one frame at a time; never rewrite an earlier frame.
- Each role emits only its owned `kind`.
- Each frame carries an increment and references large content by path/hash instead of inlining it.
- Each frame links to the previous frame with `parent_id` and `prev_hash`; `hash` is computed by the canonical algorithm in `references/messages.md`.
- A later frame is admissible only when the previous frame is `complete`.
- `LOOP` requires one bounded repair seed. The orchestrator admits the repair route; it is not an arbitrary phase jump.
- `HALT` ends the cycle.
- Reflective seeds use machine-stable levels `meta`, `meta2`, or `meta3`, corresponding to current artifact/phase repair, skill/workflow repair, or orchestrator/agent-prompt repair. Every seed is unexecuted.

## Resources

- [messages.md](references/messages.md): envelope, role-owned payloads, routing, and hash rules.
- [queue.md](references/queue.md): bounded queue wait, marketplace `reflect` invocation, and dynamic meta-level routing.
- [validate_frames.py](scripts/validate_frames.py): deterministic JSONL validator.
- [valid.jsonl](assets/examples/valid.jsonl) and [invalid.jsonl](assets/examples/invalid.jsonl): small validation fixtures.
- `agents/pmcro-messages-protocol.json`: the declarative skill agent surface. It is not the independent checker; the checker must use a separate context.

## Refuse or stop

Stop and ask for a narrower charter when the target path is unclear, a session asks to copy credentials or a full transcript by default, a role emits another role's kind, a hash chain is broken, the checker is not independent, the queue has no eligible completed checker frame, or a seed would execute automatically.
