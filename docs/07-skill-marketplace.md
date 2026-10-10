# Skill marketplace conventions

The marketplace convention in this project is generic first, specialized second.

## Default skill shape

An installable skill should normally contain:

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
├── assets/
└── tests/
```

The folders can be empty only when the skill’s manifest explicitly says so. The `agents/` folder matters because it makes the agent surface inspectable instead of hiding it in prose.

## Routing syntax

The project uses the compact routing shape:

```text
@[agent] /[plugin]:[skill]
```

For example:

```text
@skill-creator /pmcro:marketplace
@checker /pmcro:check
@figma-agent /figma:design-to-code
```

The syntax is a dispatch hint, not a permission grant. Resolution still checks the principal, plugin, version, charter, and capability scope.

## Promotion states

```text
draft -> locally validated -> independently checked -> staged -> promoted
```

The generic `skill-creator` can move a manifest into a draft folder. It cannot promote the result merely because the folder exists. The checker must validate required files, activation guidance, limits, and refusal conditions.

## Generating an actual product repository

Marketplace functionality may generate a real product repository as a bounded child artifact. The child is created from a versioned declarative template and remains tied to its parent marketplace run, owner, domain charter, source trail, source commit, depth/max-depth grant, and checker evidence.

```text
checked trail -> product manifest -> versioned template -> generated repository
             -> repository validation -> independent check -> staged -> promoted
```

The generated repository is an inspectable filesystem result, not merely a simulated package or a model response. Its manifest must identify the reused marketplace skills, generated paths, tests, assets, provenance, evidence tier, and promotion state. A marketplace run may stage the child, but it cannot self-promote, publish, widen authority, or silently add credentials and private reasoning. If generation or checking fails, the child returns to `composed` or `rejected` with one bounded next seed.

## PMCR-O plugin message contract

The local plugin registry in `.agents/plugins/marketplace.json` binds the
`pmcro` plugin's `reflect` skill to the `reflector` phase agent. The same
registry shape is used for the session marketplace constructor and the
role-owned message protocol. Each entry declares `input`, `output`, `accept`,
and `deny` fields. This keeps application adapters and training projections on
the same typed contract: a simulated MCP, MAF, terminal, provider, or code
surface may be a candidate, but it cannot become live evidence or a promoted
skill without a separate checker and policy decision.

## Marketplace federation

A remote marketplace or GitHub repository is an optional source of artifacts. The local trail should record source URL or repository ref, version, digest, and the policy decision before installation. A catalog entry is not the same thing as a trusted executable.
