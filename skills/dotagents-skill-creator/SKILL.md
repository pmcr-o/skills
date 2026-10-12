---
name: dotagents-skill-creator
description: Bootstrap or reconcile a provider-neutral PMCR-O agent skill from an immutable request. Skill Creator is the registered CREATE lifecycle authority; generated candidates remain untrusted until independent CHECK.
---

# DotAgents Skill Creator

Use this skill to create a repeatable skill workspace consumable by ChatGPT/Codex, Claude, local models, and other projections. The canonical executable source is one skill directory under `.agents/skills/`; provider/plugin files are projections, not competing sources of truth.

Use `.pmcro/` as the control-plane mirror for charter, registry, governance references, trails, checkpoints, manifests, and seeds. Do not place executable skill source in `.pmcro/`.

## Lifecycle authority

`dotagents-skill-creator` is the registered CREATE authority for canonical skills. It must not depend on a second hidden or nonexistent `create-skill` capability in order to materialize a candidate.

Creation remains bounded:

`RAW_SEED -> CREATE CANDIDATE -> INDEPENDENT CHECK -> PROMOTE/REGISTER -> LATER USE`

Generation is not trust and generation is not execution. A newly created skill stays draft-only until independent checker evidence permits promotion.

READ/RETRIEVE, UPDATE, DELETE, VERSION, INSTALL, PUBLISH, or runtime execution are separate lifecycle capabilities when the marketplace registers them. CREATE authority does not imply those authorities.

## Required skill shape

Every generated canonical skill must contain:

- `SKILL.md`
- `agents/`
- at least one PMCR-O agent that binds one identity and contains `I AM THE`, `I ORCHESTRATE`, `I PLAN`, `I MAKE`, `I CHECK`, and `I REFLECT`

The following are supported progressive-disclosure layers and are optional:

- `references/` for knowledge, rules, and mental models
- `assets/` for inert prompts, templates, examples, schemas, and static resources
- `scripts/` for deterministic executable behavior
- `tests/` for skill-specific deterministic verification

Do not create empty optional folders merely to satisfy shape. Emit an optional layer only when the declared artifact graph requires it.

## Required behavior

1. Preserve the raw seed exactly when one is supplied and record a deterministic hash for provenance.
2. Derive a bounded skill manifest from the request; do not overwrite the raw seed with a cleaned interpretation.
3. Inspect an existing marketplace or skill repository before reconciling it.
4. Materialize the candidate directly through this Skill Creator's registered CREATE implementation.
5. Default to dry-run; require explicit `--apply` or equivalent before filesystem writes.
6. Preserve unknown files. Overwrite only paths recorded as managed by an earlier Skill Creator run.
7. Keep `.pmcro/` control-plane state separate from `.agents/skills/` executable skill source.
8. Create provider projections only as projections of the canonical `.agents/skills/` source.
9. Mark generated candidates `draft-only` / `generated-unchecked` until independent CHECK.
10. Report exact managed paths and one unexecuted next seed. Never self-certify a generated child.

## Manual entrypoints

```text
python scripts/bootstrap_workspace.py --root <workspace> --skill <name> --plugin <name>
python scripts/bootstrap_workspace.py --root <workspace> --skill <name> --plugin <name> --raw-seed "<immutable request>" --apply
python scripts/bootstrap_workspace.py --root <workspace> --skill <name> --plugin <name> --with-references --with-assets --with-scripts --with-tests --apply
python scripts/discover_marketplace.py --root <existing-skill-repo>
python scripts/route_create_skill.py --catalog <catalog.json> --skill <name> --plugin <name>
python scripts/validate_workspace.py --root <workspace>
```

`route_create_skill.py` emits a typed request addressed to this Skill Creator. It is not a handoff to a second creator.

## Boundaries

This skill may stage local candidate artifacts within its declared workspace. It does not install packages, connect accounts, access credentials, publish a marketplace, or claim that provider projections are executable everywhere.

A separate checker must validate a generated child before promotion or use. Optional prompt/assets remain inert until a registered runtime consumes them; generated scripts remain untrusted until checked and later admitted for execution.

## Handoff

Return `artifactId`, canonical path, raw-seed provenance when present, generated layers, provider projections, managed paths, validation evidence, promotion state, and one unexecuted next seed. Use `PASS`, `LOOP`, or `HALT`; never self-certify the generated workspace.
