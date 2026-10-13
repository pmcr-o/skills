# ADR-0006: Claude Code is the reference provider layout

Status: accepted

## Context

PMCR-O needs provider-neutral packaging without inventing new filesystem names for concepts already standardized by mature agent tooling.

## Decision

Claude Code's marketplace, plugin, agent, skill, command, hook, and MCP component boundaries are the reference provider layout for PMCR-O projection design. PMCR-O mirrors existing component names where semantics match and adds new names only for PMCR-O-native protocol, Trail/Cycle/Frame, evidence, registry, model-lifecycle, and projection concerns.

The reference layout does not grant Claude-specific authority and does not make Claude files canonical.

## Consequences

The PMCR-O projection compiler SHOULD emit Claude-compatible `.claude-plugin/marketplace.json`, per-plugin `.claude-plugin/plugin.json`, project `.claude/agents/`, and `.claude/skills/` from canonical PMCR-O sources. Future providers map from the same canonical graph rather than from Claude output.

## Supersedes

None.
