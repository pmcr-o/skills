# MCP and Thought Transfer

The project’s short claim is:

> MCP enables Thought Transfer when it transports explicit intent, capability, artifacts, and evidence across an agent boundary.

That claim is intentionally narrower than “MCP transfers thoughts.” A protocol can move structured messages and invoke tools. It cannot establish that two agents share a mind or that a generated `I AM` voice is conscious.

## The typed bridge

```json
{
  "principal": "end-user-123",
  "entrypoint": "product-ui",
  "intent": "draft a marketable children’s story in my declared voice",
  "flow": "forward",
  "scope": {
    "tools": ["story.generate", "quality.check"],
    "sideEffects": "none",
    "maxTurns": 6
  },
  "handoff": ["draft", "quality_evidence", "assumptions", "next_seed"]
}
```

The receiving server can use the envelope to select a skill, run a bounded action, and return an artifact plus evidence. The client can append the result to the trail and decide whether to show, revise, or promote it.

## Minimal cross-session handoff

MCP or another entrypoint should carry a validated reference set, not the whole originating session. The minimum handoff is:

```json
{
  "resourceRefs": [
    {"packageId": "01-domains", "path": "docs/08-mcp-and-thought-transfer.md", "sha256": "checked", "commit": "verified"}
  ],
  "scope": {"maxTurns": 4, "sideEffects": "none"},
  "acceptance": ["resource exists", "hash matches", "checker evidence is present"],
  "nextSeed": {"level": "meta", "promptIntent": "request only the missing package", "unexecuted": true}
}
```

The receiving session requests a package only when it cannot access a declared reference. Passing a full transcript is a bounded recovery action that needs its own charter; it is not the default handoff. The orchestrator remains responsible for the high-level goal and for advancing the phase order.

The phase route is always:

```text
ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT -> new ORCHESTRATE frame
```

`PLAN` consumes validated resources and writes the bare-minimum graph. `CHECK` catches errors in a fresh context. `REFLECT` proves the earned constraint and emits one unexecuted prompt-intent seed rather than executing a repair itself.

## Backward bridge

For learning, the envelope carries checked experience into a builder:

```text
trail evidence -> MCP handoff -> lens/template update -> checker -> staged skill
```

The builder should preserve the source event IDs and distinguish a proposed rule from a verified invariant.

## Forward bridge

For product use, the envelope carries user context into a product skill:

```text
checked trail product -> MCP handoff -> identity-aware generation -> quality checker -> deliverable
```

Identity should be declared and scoped. Do not silently infer a user’s identity from an account token, copy private memories into a reusable template, or claim that an output will be a bestseller. “Best seller” is a target for evaluation and iteration, not a guaranteed result.

## Trail rule

Every MCP call that matters to the product should append:

- the calling principal and entrypoint;
- the server/tool name and version;
- the input scope and side-effect mode;
- the returned artifact or error;
- the evidence/checker result; and
- the parent trail event.

That makes MCP a bridge in the trail rather than a black box between phases.
