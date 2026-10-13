# ADR-0001: Marketplace is the canonical top-level system

Status: accepted

## Context

PMCR-O packages plugins, agents, skills, capabilities, model bindings, provider projections, evidence, and lifecycle state. Treating each provider catalog or plugin manifest as independently authoritative creates drift and conflicting system definitions.

## Decision

The PMCR-O MARKETPLACE is the canonical top-level SYSTEM.

Plugins are distributable subsystems/packages within the Marketplace. Agents are controllers. Skills are reusable capabilities. Provider-native marketplace and plugin files are projections of the canonical graph.

There MUST be one canonical marketplace composition graph. Claude, Codex, `.agents`, Ollama, MAF, MCP, A2A, OpenAPI, and gRPC surfaces MUST NOT independently widen or redefine canonical authority.

## Consequences

- Marketplace composition is modeled once and projected many times.
- Provider projections can be regenerated and checked for drift.
- Plugin registration requires checked canonical contracts before provider projection.
- A provider-specific manifest is not sufficient evidence of canonical registration.
- Existing `.agents/plugins/marketplace.json` and `plugins/*/plugin.json` surfaces must be reconciled as canonical aliases or generated projections, not competing truths.
