# `reflect` marketplace contract

## Role versus skill

The `reflector` is a PMCR-O phase agent. The marketplace skill named `reflect`
is the reusable procedure that the agent invokes. The skill has no independent
authority: it may read the checker handoff, append its own frame, and emit a
seed for a later orchestrator cycle.

## Queue wait condition

The skill consumes one queue item only when all of these are true:

- the item contains a `checker.verdict` frame;
- the frame has `status: complete`;
- `payload.independent` is `true`;
- the frame is linked to the current trail/cycle; and
- the item has not already been acknowledged or consumed by the same
  `dedupe_key`.

No eligible item means `WAIT`, not a guessed reflection. The queue can be an
in-process MAF channel, an MCP result stream, or a JSONL simulation. In every
case, the append-only `.pmcro/trails/` record remains the durable source of
truth.

## Reflection output

The skill appends one `reflector.reflect` frame whose parent is the selected
checker frame. Its `next_seed` is a messy seed for the next cycle, with:

```json
{
  "level": "meta|meta2|meta3",
  "prompt_intent": "bounded raw intent, not an execution command",
  "required_resources": ["exact package, path, commit, or frame ref"],
  "unexecuted": true
}
```

Human-facing labels are `meta`, `meta-meta`, and `meta-meta-meta`. The stable
machine labels are `meta`, `meta2`, and `meta3` so validators do not have to
parse punctuation.

## Dynamic next-cycle routing

The orchestrator uses the typed seed and current evidence to choose the next
bounded route:

| Seed | Display | Repair surface | First route target |
| --- | --- | --- | --- |
| `meta` | `meta` | current artifact or phase acceptance | maker |
| `meta2` | `meta-meta` | skill, workflow, or package contract | planner / loop-builder |
| `meta3` | `meta-meta-meta` | orchestrator, agent surface, or prompt routing | orchestrator |

This is dynamic routing over declared evidence, not an export of hidden chain
of thought and not unbounded self-modification. Every new seed starts the
normal `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT` route again.
