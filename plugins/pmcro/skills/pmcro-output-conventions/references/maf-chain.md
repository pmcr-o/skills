# MAF workflow chain

The MAF Native adapter maps each skill surface to a typed executor. Edges carry
the output envelope, not an unbounded conversation. The graph builder should
connect only declared edges and expose the final reflector output.

```text
orchestrator -> planner -> maker -> checker -> reflector
       \-> catalog/filesystem/MCP dependencies under their own grants
```

Use workflow checkpoints for resumable runtime state. Keep role state in the
message or an explicitly named, scope-aware state store. The checker must not
receive the maker's private conversation as an implicit shared transcript; give
it the plan, artifact refs, acceptance cases, and evidence it needs.

For simulation, use the same graph and envelope but replace runtime adapters
with labelled stubs. The console projection may say that a MAF executor or
`.NET` service would be called; it must not say that it was called. The
independent checker compares a future execution trace to the simulated action
ids and expected outputs.

Primary runtime references:

- `https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/`
- `https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints`
- `https://learn.microsoft.com/en-us/agent-framework/workflows/observability`
