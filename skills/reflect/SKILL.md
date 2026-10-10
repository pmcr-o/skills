---
name: reflect
description: Wait for a completed independent PMCR-O checker frame, record one earned constraint, and emit one unexecuted next seed for the orchestrator. Use as the reflector agent's post-check marketplace skill.
---

# PMCR-O `reflect`

`reflect` is the marketplace skill invoked by the `reflector` phase agent. It
does not replace that agent and it does not certify work. It waits for a
completed `checker.verdict`, records the evidence-weighted learning boundary,
and returns one new messy seed as raw prompt intent.

## Contract

1. Read a bounded queue or trail view. Accept only a `checker.verdict` frame
   whose status is `complete` and whose `independent` field is `true`.
2. If no eligible checker frame exists within the finite scan cap, return
   `WAIT` and make no frame, file, or verdict.
3. Invoke the reflector logic once for the selected checker frame. The result
   is one `reflector.reflect` frame linked to that checker frame.
4. Preserve the seed as messy input for the next cycle. The next orchestrator
   must re-derive intent from it; it must not treat the seed as a command or
   jump directly to MAKE, CHECK, or REFLECT.
5. Emit exactly one unexecuted seed at the smallest level that explains the
   finding: `meta`, `meta2` (`meta-meta`), or `meta3`
   (`meta-meta-meta`).

The durable trail is authoritative. A queue acknowledgement is only transport
bookkeeping. It is not a checker verdict, approval, promotion, or permission
to execute the seed.

## Manual simulation

From this directory:

```bash
python3 scripts/reflect.py \
  --queue assets/examples/checker-queue.jsonl \
  --level meta2 \
  --prompt-intent "Re-open the skill handoff as a raw seed and tighten its contract." \
  --required-resource pmcro-messages-protocol

python3 scripts/route_seed.py path/to/reflect-frame.json
```

The scripts are deterministic filesystem simulations. A separate checker
session must validate the resulting frame before any generated artifact is
promoted.

## Refusals

Do not synthesize a checker result, approve the maker's output, execute a next
seed, erase an earlier trail frame, consume credentials, or turn a full
transcript into a default handoff.
