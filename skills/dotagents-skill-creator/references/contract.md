# DotAgents workspace contract

## Source of truth

The canonical implementation of a skill is:

```text
.agents/skills/<skill>/
  SKILL.md
  agents/agent.json          # provider-neutral contract
  agents/openai.yaml         # one provider adapter
  scripts/
  references/
  assets/
  tests/
```

## The skill template is the contract

The creator's child template has two synchronized views of the same design:

- `SKILL.md` explains the workflow and progressive-disclosure rules to a
  human or language model.
- `agents/agent.json` declares the machine-facing `inputs`, `outputs`,
  `accept`, `deny`, tools, limits, and authority.

The `Input` section is therefore not a loose prompt convention. It is a
template slot. The plugin catalog and a MAF executor may inspect it before
invocation, while the checker can reject a handoff that supplies undeclared
fields, missing resources, or a widened grant. The default output contract is
shared by JSON, `.NET` console, and trail projections so the same skill can be
composed without rewriting its semantics for each provider.

`plugins/<plugin>/` and `.agents/plugins/marketplace.json` are projections that
point at the canonical directory. They must not contain a second editable
copy of the skill.

## Existing-marketplace loop

Before creating a skill, scan the selected source repositories with
`discover_marketplace.py`. The scan is read-only and produces a catalog of
existing skills, required-folder status, agent files, and hashes. A local
checkout of `dotnet/skills` is treated like any other upstream source.

Every creation request then emits `.agents/requests/create-skill/*.json` with
`requiredInvoker: "dotagents-skill-creator"` and
`creatorAuthority: "dotagents-skill-creator"`. Skill Creator is the registered
CREATE lifecycle authority and materializes the candidate directly; it MUST NOT
depend on a second hidden or nonexistent `create-skill` capability. The handoff
may identify an existing compatible skill, but it never grants permission to
copy, overwrite, register, promote, or use it.

## Repeatability

`dotagents.manifest.json` records the owner, version, component id, canonical
path, projections, and exact `managedPaths`. A later run may update a file only
when it is listed as managed or its contents are byte-for-byte identical. An
unknown conflicting file is a `HALT`, not an invitation to overwrite it.

`--clean-managed` removes only the selected component paths from the previous
manifest. It never recursively deletes the workspace, a repository, unknown
files, credentials, caches, or files outside the root.

## Control-plane mirror

`.pmcro/charter.json` declares the workspace domain and bounded operations;
`.pmcro/registry.json` maps capability, governance, and trail roots; and
`.pmcro/governance/` records re-verifiable policy-boundary references. The
Microsoft Agent Governance Toolkit entry is an implementation reference for
policy/tool interception and ADRs, not a replacement for PMCR-O orchestration
or a source of runtime authority. The subfolders `trails/`, `checkpoints/`,
`manifests/`, and `seeds/` hold append-only or staged evidence. This mirrors a
vendor plugin layout without making the vendor directory authoritative. The
loader must validate the manifest, charter, governance reference, and checker
evidence before executing a generated project.

## Evidence tiers

- `pattern-valid`: the manifest and folder contract validate.
- `execution-verified`: the generated validator and tests ran successfully.
- `production-verified`: the declared target environment accepted the result.

Running the script locally cannot prove a remote provider can load a plugin.
Provider adapters remain explicit and must be checked by that provider.

## Capability boundary

The constructor is a local staged generator. It has no network, package
installation, account, secret, publish, or deployment authority. Marketplace
promotion is a later PMCR-O child run with a separate checker.
