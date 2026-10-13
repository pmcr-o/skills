# PMCR-O MARKETPLACE 1.0

Status: candidate

Normative terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are used as requirements.

## 1. Canonical hierarchy

A PMCR-O marketplace MUST be the top-level distributable system. It MUST contain or reference one or more plugins. A plugin MUST be a distributable subsystem and MAY contain agents, skills, commands, hooks, workflows, evals, scripts, binaries, MCP bindings, and other declared components.

`MARKETPLACE -> PLUGIN -> COMPONENTS`

## 2. Canonical filesystem authority

The canonical marketplace manifest MUST be `.pmcro-plugin/marketplace.json`.

A canonical plugin manifest MUST be located at `plugins/<plugin>/.pmcro-plugin/plugin.json`.

The `.pmcro/` directory MUST contain PMCR-O control-plane state such as protocol, registry, evidence, models, training contracts, and projection profiles.

Portable reusable skills SHOULD remain under `skills/<skill>/` with `SKILL.md` and at least one machine-readable agent under `agents/`.

## 3. Authority

Canonical manifests MUST declare canonical authority explicitly. Provider-native outputs MUST NOT declare canonical authority. Existing compatibility manifests MAY remain in place only when they identify their canonical source using `projectionOf` or an equivalent immutable reference.

## 4. Progressive disclosure

A skill's required core is `SKILL.md + agents/`. `references/`, `assets/`, `scripts/`, and `tests/` are optional layers and MUST NOT be created empty solely for conformity.

A plugin SHOULD expose only component roots and components that are required by its contract.

## 5. Promotion

A newly generated marketplace or plugin contract MUST begin as candidate or generated-unchecked state. It MUST NOT be promoted or registered until independent CHECK evidence exists.

## 6. Provider projections

Provider projections MUST be derived from the canonical marketplace and plugin graph. They MUST preserve provenance and MUST NOT invent capabilities, tools, models, grants, or lifecycle state.

A provider projection MAY copy portable skill packages into a provider-native package tree, but the copied material remains a projection.

## 7. Claude reference projection

The Claude projection SHOULD emit:

- `.claude-plugin/marketplace.json` at the projected marketplace root;
- `plugins/<plugin>/.claude-plugin/plugin.json` inside each projected plugin;
- plugin `agents/` and `skills/` component directories where declared;
- project `.claude/agents/` and `.claude/skills/` surfaces when requested;
- a thin `CLAUDE.md` bootstrap that identifies canonical PMCR-O authority.

## 8. Validation

Deterministic conformance MUST verify canonical-path uniqueness, provider non-authority, valid component references, skill core requirements, and reproducible projection output.
