# Local execution and adapter boundaries

“Full terminal access” is best modeled as a capability surface, not as an unqualified promise. A local runner can have broad technical reach while a specific phase still receives a narrow grant.

## Capability grant

A phase envelope should constrain at least:

| Dimension | Example |
| --- | --- |
| Domain | local files, Git, Docker socket, Figma API |
| Paths | `thought-transfer-pmcro/**` |
| Tools | read, write, test, commit |
| Time/turns | `maxTurns: 8` |
| Recursion | `maxChildDepth: 2` |
| Side effects | none, staged, or approved |
| Evidence | command result, diff, test output, or API response |

The machine may be capable of more than the role is allowed to do. The difference is the point of the envelope.

## Docker

Docker can provide a reproducible execution boundary. The safe sequence is:

1. describe the image and mounted paths in the charter;
2. run a dry-run or read-only fixture;
3. capture the command, image digest, output, and exit status;
4. let a checker inspect the evidence; and
5. promote side effects only after policy approval.

This repository does not invoke Docker. It documents the contract so a later adapter can be tested against the same handoff shape.

## Microsoft Agent Framework (MAF)

MAF can be treated as an execution adapter for the role graph: executors represent phases, messages carry envelopes, and checkpoints map to trail events. The adapter must preserve `contextId`, `maxTurns`, scope, and evidence instead of hiding them in framework internals.

### MAF-native evolution constraint

The future agent system is constrained to the native MAF surface and to the version that the project pins. A MAF adapter must therefore:

1. read the pinned `Microsoft.Agents.AI.Workflows` version from `Directory.Packages.props` before selecting APIs;
2. use a custom `WorkflowBuilder` graph for PMCR-O so the independent checker does not inherit the maker conversation through opaque sequential orchestration;
3. carry role state in messages or checkpoint state, write JSON checkpoints, and verify executor identities when resuming; and
4. stop or emit an unexecuted `meta-meta` seed when the pinned MAF version lacks a required capability, rather than inventing native support or hiding a parallel runtime behind the adapter.

This repository currently documents the boundary and has no `Directory.Packages.props` or runnable .NET workflow project. The constraint is a future compatibility rule, not a claim of runtime support today.

### Native runtime and cognitive trail split

If a future implementation adopts an Anthropic-style agentic design pattern, use native MAF for the executable runtime: workflow topology, role executors, tool calls, bounded turns, and checkpoint/resume. Use Thought Transfer for the cognitive/control plane: declared intent, validated resources, PMCR-O role frames, cross-session handoff, provenance, reflection, and next seeds. Thought Transfer is not a hidden second workflow engine, and MAF is not a substitute for the cognitive trail. The boundary stays inspectable and independently checkable.

## Harness and CodeAct

Harness and CodeAct-style execution can share one action schema:

```json
{
  "actionId": "act-001",
  "kind": "shell",
  "command": "python3 scripts/validate_repo.py",
  "mode": "dry-run-or-execute",
  "scope": "thought-transfer-pmcro/**",
  "result": {"exitCode": 0, "evidenceRef": "check-0001"}
}
```

Simulation mode validates the action shape with side effects disabled. Execution mode runs the command and records the actual evidence. The same IDs and limits make the two modes comparable.

## Figma

A connected Figma account is an entrypoint and a possible design-domain capability. It is not an automatic right to edit or publish. A Figma phase should state whether it can read design context, propose changes, write to a draft, or publish. `figma` is therefore an adapter in the same envelope model as local Git or Docker.

## MCP as the transfer boundary

MCP can enable Thought Transfer when it carries a typed, provenance-linked envelope between a caller and a domain server. The useful unit being transferred is explicit work state:

```text
principal + intent + scope + action + evidence + handoff
```

An MCP tool can expose a design operation, a trail append, a checker, or a product-generation capability. The protocol does not by itself make the receiving agent share the caller’s mind or grant unrestricted authority. Each tool call still needs an entrypoint, capability scope, side-effect mode, and evidence result.

The backward flow can use MCP to send checked evidence into a skill/template builder. The forward flow can use MCP to send a user-declared identity and intent into a product generator and return a checked deliverable. Keep the two flows distinguishable in the trail so learning artifacts are not confused with customer outputs.
