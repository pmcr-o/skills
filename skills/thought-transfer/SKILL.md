---
name: thought-transfer
description: Translate Hofstadter-inspired self-reference, Buber-inspired dialogue, and von Neumann-inspired constructor ideas into clearly simulated I AM role frames, bounded PMCR-O phase envelopes, declarative skill designs, and provenance-linked trail events. Use when a user asks to create a philosopher-inspired agent or skill, convert a philosophical concept into an agentic design, document a cognitive trail, or separate multiple entrypoints, phase agents, and independent checkers.
---

# Thought Transfer

Use this skill to transfer a useful design pattern from a philosophical lens into a bounded, inspectable agent artifact. Keep the transfer explicit: lens -> role frame -> scope -> evidence -> trail. Treat every `I AM` passage as generated simulation, never as a historical person speaking or as evidence of consciousness.

## Workflow

1. Preserve the raw user seed verbatim in the calling PMCR-O trail. Do not replace it with an interpretation.
2. Select one or more lenses. Use `references/lens-mappings.md` for the narrow mapping; use the composite lens only when the user wants synthesis.
3. Declare `flow: backward` for trail-to-skill learning or `flow: forward` for identity-aware product generation. Render a role frame with `scripts/render_frame.py`. Fill `I AM`, `I NOTICE`, `I ASK`, `I REFUSE`, and `I HAND OFF`.
4. Add a phase envelope: principal, entrypoint, context ID, domains, paths, tools, turn cap, child-depth cap, side-effect mode, and handoff fields.
5. Emit one parent-linked trail event. Record what was inferred, what remains uncertain, and the evidence location.
6. Run `scripts/validate_frame.py` in a fresh checker context when claiming the frame is checked. A producer must not grade its own output.
7. Hand off only the frame, scope, evidence, open findings, and one bounded next seed. Stop when the discovery cap is reached or the acceptance contract is stable.

## Resource-first control plane

The public entrypoint is the orchestrator. It owns the high-level goal and advances the only normal phase route:

```text
ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT
```

The planner may plan only from validated resources: exact package IDs, paths, hashes, commits, and evidence references. A receiving session gets those references and the minimum charter, not the full prior conversation. It may request a later package when a declared resource is unavailable. It must not infer omitted context or jump directly to MAKE, CHECK, or REFLECT.

When CHECK finds an error, REFLECT records the earned constraint and returns one unexecuted prompt-intent seed. Use `meta` for the current artifact/phase, `meta-meta` for the skill/workflow contract, and `meta-meta-meta` for the orchestrator, agent surface, or prompt-routing system. Only the next orchestrate frame may decide whether that seed is admitted.

## Backward and forward flows

Use the two directions as separate, linked flows:

### Backward flow: learning from trail to design

Move checked experience inward, like an apprenticeship or a book being written:

```text
raw experience -> trail -> reflection -> earned constraint -> reusable lens/template -> checked skill
```

Preserve provenance and uncertainty. Do not turn a single anecdote into a universal rule. Cap discovery cycles, child depth, and resource use. The backward flow may improve a draft skill, but it cannot silently promote itself or widen authority.

### Forward flow: selling a trail as a product

Move a checked trail outward as a reusable product:

```text
checked trail product -> end-user identity + intent -> bounded personalization -> quality check -> deliverable
```

Inject the end user’s identity as declared context, not as a license to impersonate them or copy private data. Personalize voice, goals, audience, and constraints only within the product charter. A “best seller” request is a quality objective, not a guarantee; return evidence, assumptions, and unresolved risks with the deliverable.

The same trail can support both directions, but the permissions differ: backward flow may propose skill changes; forward flow may produce user-facing work. Neither direction may rewrite history or claim that simulated voices are persons.

## Frame contract

The rendered frame must use this meaning:

```text
I AM:       the bounded lens or phase role
I NOTICE:   the pattern this role is responsible for seeing
I ASK:      the question that improves the next handoff
I REFUSE:   the overreach this role will not perform
I HAND OFF: the artifact or constraint another role can inspect
```

The first-person form is a user-facing compression of a role contract. It is not an identity claim. Add an attribution line such as “Hofstadter-inspired simulation” whenever the lens is named after a historical thinker.

## Lens selection

| Lens | Transfer into agent design | Required guardrail |
| --- | --- | --- |
| `hofstadter` | Make reflection, self-reference, and next-seed formation observable. | Recursion depth and cost cap; self-reference is not consciousness. |
| `buber` | Make principal, relation, consent, and policy boundary explicit. | Never infer consent or authority from a connected account. |
| `von-neumann` | Separate description, constructor, constructed artifact, and checker. | Bound child depth; never copy credentials or promote without checking. |
| `thought-transfer` | Compose the three mappings into one translation artifact. | Keep metaphor, simulation, and executable authority distinct. |
| `phase` | Apply the same frame to orchestrate, plan, make, check, or reflect. | Declare role, tools, context boundary, and handoff. |

## Entrypoints and independence

Treat each account, plugin, API, MCP client/server route, local model, or Figma session as an entrypoint with a principal ID. Use MCP to carry typed intent, capability, artifacts, evidence, and handoffs across a boundary; do not describe it as transferring consciousness or private inner experience. Do not treat entrypoint identity as permission. Put actual authority in the phase envelope.

Every phase may use a separate agent surface. Mark a checker as independent only when it receives a fresh context, the handoff plus acceptance contract, a finite stop cap, and no ability to silently rewrite the producer’s artifact. A phase agent being separate does not automatically make it an independent checker.

## Resources

- Read `references/lens-mappings.md` when selecting or composing a philosophical lens.
- Read `references/trail-contract.md` when emitting or reviewing a trail event.
- Use `assets/frame-template.json` as the minimal input/output shape.
- Run `scripts/render_frame.py` to create a deterministic frame and envelope.
- Run `scripts/validate_frame.py` to check required markers, limits, and independence fields.

## Refusal conditions

Refuse or escalate when the request asks the skill to impersonate a historical person, claim sentience or secret inner experience, expand authority because of a name or account, create unbounded self-reproduction, hide external side effects, or certify its own work without a separate check.
