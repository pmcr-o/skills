---
name: desktop-commander
description: Use the Remote Desktop Commander connector as a bounded filesystem and PowerShell runtime adapter for PMCR-O workflows. Read-only discovery is the default; writes and processes require scoped grants.
---

# Desktop Commander adapter

This skill exposes a generic connector surface that can specialize into domain
children such as `sample-child`, `dotnet-inspect`, or a repository marketplace
adapter.

Supported operations:

- `list`/`read`/`search`: read-only discovery of a declared path;
- `process`: invoke a declared PowerShell or native command with a finite
  timeout and capped output;
- `write`: write only to an explicitly authorized project path;
- `handoff`: return exact paths, command output, exit state, hashes, and a next
  seed to the orchestrator.

The adapter does not provide delete, credential, publish, or arbitrary-shell
authority. A filesystem listing does not imply write or process permission.
Simulation reports predicted paths and commands with `simulation: true` and
`verified: false`. A fresh checker reruns the validator and any declared proof.

PowerShell marketplace skills provide mechanics such as filesystem discovery,
one-script invocation, auth-status checks, or a domain validator. The adapter
provides mechanics; PMCR-O still owns routing, caps, evidence, and verdicts.
