# Queue and `reflect` skill boundary

The message queue is a transport surface; the PMCR-O trail is the durable
control plane. A queue item may arrive from a native MAF channel, an MCP result
stream, another account's handoff, or a JSONL simulation. None of those
transports grants authority or replaces the append-only trail.

## Post-check wait

The `reflector` agent invokes the marketplace skill named `reflect` only after
it observes a complete `checker.verdict` with `independent: true`. It scans a
finite number of queue items. If no eligible item is present, it returns
`WAIT` and leaves the trail unchanged. It never manufactures a verdict from a
maker result or a timeout.

After the skill appends one `reflector.reflect` frame, the transport can be
acknowledged using a stable queue/deduplication key. Acknowledgement means
"delivered" only; it does not mean `PASS`, promotion, or seed execution.

## Dynamic seed routing

The reflector emits one unexecuted messy seed. The next orchestrator cycle
re-derives true intent from that seed and selects the smallest repair surface:

| Stable level | Human label | Route target |
| --- | --- | --- |
| `meta` | `meta` | maker: artifact/phase repair |
| `meta2` | `meta-meta` | planner or loop-builder: skill/workflow repair |
| `meta3` | `meta-meta-meta` | orchestrator: agent/prompt/control-plane repair |

This is recursive in the useful sense: a next seed may itself be messy input
for another bounded cycle. It is not recursive execution. Every cycle starts
at `ORCHESTRATE`, revalidates resources, and gets a fresh checker context. A
finite depth/call/turn cap stops escalation; the unexecuted seed is retained
when the cap is reached.

The router may expose the typed decision, selected target, caps, and evidence
references. It must not expose or require hidden chain-of-thought.
