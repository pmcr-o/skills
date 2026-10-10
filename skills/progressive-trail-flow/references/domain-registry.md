# Progressive domain registry

The registry is a routing aid, not a catalog of permissions. A domain entry tells the flow which references to load, which artifact shape to expect, and which checker can inspect the handoff.

## Minimum entry

```json
{
  "id": "domain-name",
  "entrypoints": ["@agent /plugin:skill"],
  "iAm": {
    "notice": "bounded pattern",
    "refuse": "bounded overreach",
    "handOff": "inspectable artifact"
  },
  "scope": {"domains": [], "tools": [], "sideEffects": "none"},
  "loadWhen": ["trail phrase or artifact"],
  "artifacts": ["file or schema"],
  "checker": "checker-id"
}
```

## Known domains from the trail corpus

- **dotnet-skills:** production skill layout and conventions. Treat the recorded `SKILL.md`, `agents/`, `scripts/`, `references/`, and `assets/` shape as a compatibility target, then verify the current upstream repository before relying on it.
- **pmcro:** the five-phase control loop, message convention, intent envelopes, and independent checker.
- **mcp:** typed transport for intent, capability, artifact, evidence, and handoff; not a mind-transfer mechanism.
- **maf:** native MAF workflow/executor adapter that preserves phase context, limits, pinned package compatibility, and checkpoints; if the pinned version cannot provide a capability, stop or emit an unexecuted `meta-meta` seed.
- **figma:** design-domain adapter with account/entrypoint separation and explicit read/draft/publish scope.
- **harness-codeact:** action execution adapter with dry-run parity and command evidence.
- **marketplace:** discovery, version, digest, promotion, and catalog checks.

When a trail names an unknown domain, create a candidate entry with `status: undiscovered` and stop before invoking it. Discovery is not permission.
