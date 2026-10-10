---
name: dotagents-skill-creator
description: Bootstrap a provider-neutral agent-skill workspace from a declarative manifest. Use when creating or reconciling a personal .agents/skills repository, plugin marketplace projection, repeatable skill template, or local-model-friendly agent surface. The skill defaults to dry-run, preserves unknown files, and prunes only paths it previously owns.
---

# DotAgents Skill Creator

Use this skill to create a repeatable skill workspace that can be consumed by
ChatGPT/Codex, Claude, or a local Ollama agent. The canonical source is one
skill directory under `.agents/skills/`; provider and plugin files are typed
projections, not copied sources.

Use `.pmcro/` as the control-plane mirror: charter, registry, governance
references, trails, checkpoints, manifests, and next seeds. Do not put
executable skill source in `.pmcro/`; keep it under `.agents/skills/`. The
bundled Microsoft Agent Governance Toolkit entry is a re-verifiable reference
for policy/tool boundaries and ADR practice; it does not grant authority or
replace PMCR-O orchestration, checker, or trail semantics.

## Required behavior

1. Emit a `skill.create.request` message before every PMCR-O skill lifecycle.
   It is the authoring gate for `ORCHESTRATE -> PLAN -> MAKE -> CHECK ->
   REFLECT`, not a second untracked prompt. Include request ID, trail/cycle,
   plugin, skill, description, purpose, scope, validated resources, required
   folders/files, sample-prompt reference, message contract, and mode.
2. Preserve the raw request and derive a small manifest: workspace root,
   skill name, plugin name, version, owner, and requested operation.
3. Scan any existing marketplace or skill repository before writing. This
   includes a local checkout of `dotnet/skills`.
4. Route every new-skill request through the existing `create-skill` skill.
   This package emits a handoff request; it does not silently replace that
   skill. If the required creator is unavailable, stop with `HALT`.
5. Inspect the target before writing. The default is a dry-run.
6. Apply only with an explicit `--apply`/equivalent flag.
7. Create the `.pmcro/` control-plane foundation, including the declared
   governance reference, and link it to the same managed manifest.
8. Create the canonical skill with `SKILL.md`, `agents/`, `scripts/`,
   `references/`, `assets/`, and `tests/`; every skill must contain an agent
   manifest, validator, example documentation, and sample prompts.
9. Create provider-neutral `agents/agent.json`, an OpenAI adapter, a generic
   marketplace index, and a Claude-style marketplace projection.
10. Reconcile repeated runs from `dotagents.manifest.json`. Overwrite only
   previously managed files; refuse an unknown conflicting file.
11. `--clean-managed` may remove only the selected component's recorded paths.
   Never delete a repository, credentials, caches, or files outside the
   recorded managed set.
12. Run the generated validator and report exact paths, hashes, status, and one
   unexecuted next seed. A simulation is not runtime proof.
13. Publish `references/sample-prompts.md` with short, concrete copy/paste
    starters. Prompts demonstrate intent and expected output; they do not grant
    authority, add tools, or execute automatically.

## Manual entrypoints

From this skill's directory:

```text
python scripts/bootstrap_workspace.py --root <workspace> --skill <name> --plugin <name>
python scripts/bootstrap_workspace.py --root <workspace> --skill <name> --plugin <name> --apply
python scripts/discover_marketplace.py --root <existing-skill-repo>
python scripts/route_create_skill.py --catalog <catalog.json> --skill <name> --plugin <name>
python scripts/validate_workspace.py --root <workspace>
```

On Windows, pass `--root A:\\agent-skills` or another user-selected workspace.
On other systems use a native path. A provider can invoke the same Python
entrypoint; the JSON manifest is the portable contract. If `A:` is not mapped,
stop at the local staged artifact and report the destination handoff instead of
silently choosing another drive.

For an existing repository, discovery and the `create-skill` handoff are
mandatory inputs to the make phase. The loop may reuse a compatible upstream
skill through an adapter, but it must still invoke `create-skill` for the new
canonical skill shape.

The request message schema is `../../.pmcro/protocol/skill-create-message.schema.json`.
The message and the generated files are both trail evidence; a marketplace
registration is a post-check projection, not an authoring shortcut.

## Boundaries

This skill creates a staged local workspace. It does not install packages,
connect accounts, publish a marketplace, access credentials, or claim that a
plugin projection is executable by every provider. A separate checker must
validate a generated child before promotion.

## Handoff

Return `artifactId`, canonical path, plugin projections, managed paths,
validation evidence, conflicts, provider adapters, promotion state, and one
unexecuted next seed. Use `PASS`, `LOOP`, or `HALT`; never self-certify a
generated workspace.
