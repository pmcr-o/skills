# Progressive trail flow

The trail does more than remember work. It can teach the system which domains exist, which skill shape they use, and which next transformation is allowed. That learning must remain progressive and evidence-bearing.

## Trail as Product

A checked trail is a product source, not merely a log. Its reusable product is the validated pattern—intent, constraints, role frames, evidence, corrections, and next seed—projected into the smallest audience-appropriate view. A trail can become a skill, template, evaluation, benchmark, catalog entry, training candidate, or generated product repository only through provenance, redaction, independent checking, and staged promotion.

```text
raw -> redacted -> structured -> checked -> staged -> published -> derived
```

## Domain-aware `I AM`

Each domain can expose a bounded `I AM` surface:

| Domain | `I AM` meaning | Handoff |
| --- | --- | --- |
| dotnet-skills | “I AM the production skill layout and convention checker.” | Validated skill tree |
| PMCR-O | “I AM the phase and trail contract.” | Intent, verdict, next seed |
| MCP | “I AM the typed bridge across a capability boundary.” | Tool result and evidence |
| MAF | “I AM the workflow/checkpoint adapter.” | Phase output and checkpoint |
| Figma | “I AM the design-domain surface with explicit account scope.” | Design artifact and scope evidence |
| Harness/CodeAct | “I AM the bounded action executor.” | Action result and exit evidence |
| Marketplace | “I AM the version and promotion gate.” | Checked skill offer |

For an Anthropic-style agentic runtime, the intended implementation split is explicit: native MAF executes the bounded role graph, while Thought Transfer carries the cognitive/control-plane trail. The latter records intent, validated resources, evidence, cross-session handoff, and reflection; it does not expose hidden reasoning or replace the runtime.

These are role frames, not claims that a repository, protocol, or tool is conscious.

## Learning from the trail

The backward projection is:

```text
checked trail -> domain discovery -> redacted candidate -> independent review -> skill/template update
```

The trail remains authoritative for what happened. The candidate row is a derived training example and must keep `source_event_ids`, parent IDs, checker evidence, and redaction metadata.

### Fine-tuned quality from trails

Trail-derived quality comes from the constraints and evidence captured around an attempt: exact source events, role boundaries, corrections, failure modes, checker verdicts, outcome tier, and redaction status. More transcript volume is not automatically better. A failed or simulated trail can teach a labeled counterexample or design pattern, but only an authorized, redacted, provenance-linked, independently checked candidate can move toward a training or marketplace product.

The message convention is part of the learned interface:

```text
@agent /plugin:skill "intent" #trail:id
```

The JSON frame is the record; the spoken line is a projection that makes the route usable across agents and sessions.

## Progressive domain loading

The flow should not load every marketplace skill for every request. It should:

1. read the seed and domain hint;
2. resolve one registry entry;
3. validate the exact package/path/hash/commit references;
4. load one reference set;
5. run a deterministic script; and
6. hand the candidate to a separate checker.

When work crosses sessions, transfer the validated resource references, charter, acceptance evidence, and one unexecuted seed. Do not copy the full conversation unless the receiving session cannot reach a required resource and the orchestrator opens a recovery charter.

## Meta-level next seeds

Reflection chooses the smallest repair level that explains the checker finding:

| Level | Repairs | Example prompt intent |
| --- | --- | --- |
| `meta` | Current artifact or phase acceptance | “Repair the missing manifest field and rerun the bounded checker.” |
| `meta-meta` | Skill, workflow, or package contract | “Tighten the skill handoff so the manifest field is required before MAKE.” |
| `meta-meta-meta` | Orchestrator, agent surface, or prompt-routing system | “Change the control plane so PLAN can consume only validated resources.” |

The seed is a prompt intent for the next `@orchestrator /pmcro:orchestrate` call. It is not an automatic phase jump or an instruction for the reflector to repair its own finding.

## Reflector agent and marketplace `reflect`

The reflector is a phase agent, while `reflect` is the reusable marketplace
skill it invokes. The reflector waits for a completed independent checker
frame; it does not infer a verdict from a maker frame. When the checker frame
is available, `reflect` appends one reflection frame and emits one unexecuted
seed. The queue is only a transport adapter; the append-only trail remains the
source of truth.

Every seed is also a new messy seed. The next orchestrator cycle treats it as
raw input, re-derives the true intent, validates its resources, and starts the
normal route again. `meta`, `meta-meta`, and `meta-meta-meta` are routing
levels, not permissions to skip phases or to expose hidden reasoning.

This is especially important for local models. Required `scripts/`, `references/`, and `assets/` folders are not decoration: scripts execute repeatable work, references hold rules, and assets hold registries/templates.

## Forward product projection

The forward flow starts from a checked trail product and accepts declared end-user identity and intent. It can generate a personalized book, design, workflow, or other deliverable. Identity remains scoped, private data is not silently promoted into training, and “best seller” remains a quality objective—not a promise.
