# PMCR-O PROJECTION 1.0

Status: candidate

Normative terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are used as requirements.

## 1. Source

A projection MUST read canonical PMCR-O marketplace, plugin, agent, skill, protocol, or model contracts. A projection MUST NOT use another provider projection as semantic authority.

## 2. Determinism

Given the same canonical inputs and projection profile, a projection compiler MUST produce semantically equivalent output. Generated provider files SHOULD be stable in path, component identity, and ordering.

## 3. Non-widening authority

Projection MUST NOT grant new tool, capability, transport, model, credential, network, or execution authority. Provider defaults MUST NOT be interpreted as PMCR-O grants.

## 4. Provenance

Generated output MUST identify its canonical source either in machine-readable projection evidence or in the rendered provider surface. Projection evidence MUST include provider, canonical marketplace reference, canonical plugin reference, generated paths, and non-authority status.

## 5. Claude Code projection

Claude marketplace output MUST use `.claude-plugin/marketplace.json` and SHOULD declare the Claude marketplace schema URL.

Claude plugin output MUST use `plugins/<plugin>/.claude-plugin/plugin.json` and MAY project declared canonical agents to `agents/*.md` and portable skills to `skills/<skill>/SKILL.md` packages.

Project-level Claude output MAY project role agents into `.claude/agents/*.md` and portable skills into `.claude/skills/<skill>/`.

Generated Claude agent markdown MUST state that it is a projection and MUST reference the canonical PMCR-O agent contract.

## 6. Failure

Missing canonical manifests, missing skill `SKILL.md`, repository-escaping source references, duplicate component identities, or canonical/provider authority conflicts MUST halt projection.

## 7. Promotion

Successful generation is not registration or promotion. Independent CHECK MUST evaluate generated output before any provider projection is treated as usable marketplace state.
