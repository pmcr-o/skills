# Skill input is a reusable template contract

The generic `create-skill` shape is not only a folder scaffold. It is a
declarative contract that every generated child skill can project into a
provider, plugin, MAF workflow executor, local model, or marketplace entry.

```text
raw intent
   -> agents/agent.json: inputs + scope + grants
   -> SKILL.md: procedure + progressive disclosure
   -> output envelope: artifact + evidence + status
   -> checker handoff
```

## Two synchronized views

| Surface | Job | Authority |
| --- | --- | --- |
| `SKILL.md` | Explain how the skill behaves and what it refuses | Human/model-readable procedure |
| `agents/agent.json` | Declare inputs, outputs, accept/deny rules, tools, limits, and scope | Machine-facing invocation contract |
| `plugins/*/plugin.json` | Discover the skill and its dependencies | Marketplace projection |
| `templates/skill-output-envelope.json` | Normalize every handoff | Shared output contract |

The `Input` section is therefore a template slot, not an invitation to append
free-form prompt text. A generated skill may add domain fields, but it must
change the agent manifest, the readable skill instructions, the catalog
projection, and the checker fixture together.

## Generic baseline

The creator template starts with:

```json
{
  "inputs": ["intent_envelope", "validated_resources", "workspace_root"],
  "outputs": ["artifact", "evidence", "next_seed"],
  "accept": ["declared inputs are present", "evidence is attached", "checker handoff is explicit"],
  "deny": ["credential access", "unbounded recursion", "simulation as runtime proof", "self-certification"]
}
```

This is a scaffold, not permission to use every tool. The caller's scope,
resource references, side-effect mode, and PMCR-O phase still govern the
invocation. The output is always labeled `simulation=true` and
`verified=false` until a separate checker has direct evidence.

## .NET and MAF projection

The same input contract can be bound to a typed `.NET` record or a MAF
executor. The projection changes the transport and rendering, not the
acceptance semantics:

- JSON is the machine interchange form.
- `.NET` console output is a labeled human projection.
- Trail frames preserve parent IDs, evidence, and the unexecuted next seed.

The generic CRUD skill applies the same pattern to a versioned
`PmcroResource<TId,TVersion>` base model. It does not turn a template into an
execution grant or allow an update to silently overwrite the previous version.
