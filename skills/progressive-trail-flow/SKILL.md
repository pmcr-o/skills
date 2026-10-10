---
name: progressive-trail-flow
description: Progressively discover domain skills from checked PMCR-O trails, project eligible trail events into redacted training-data candidates, and route the same evidence backward into reusable skill design or forward into identity-aware products. Use when trails mention dotnet-skills, MCP, MAF, Figma, marketplaces, local models, training data, or a user asks to turn a cognitive trail into a product or learning loop.
---

# Progressive Trail Flow

Use this skill as the flow controller around `thought-transfer`. Keep the trail as the source archive and create derived projections only after checking eligibility, provenance, privacy, and flow direction. Do not treat a raw transcript, an open loop, or a simulated `I AM` passage as training truth.

## Progressive workflow

1. Preserve the raw seed and parent trail IDs. Never replace the source with a summary.
2. Discover the smallest relevant domain set from `assets/domain-registry.json`. Start with the domain explicitly named by the trail; add another domain only when the handoff requires it.
3. Load only the selected domain’s reference material. Use `references/progressive-disclosure.md` for local-model-friendly loading.
4. Choose exactly one flow:
   - `backward`: checked experience -> constraint -> training candidate -> reusable skill/template;
   - `forward`: checked trail product -> declared user identity and intent -> personalized deliverable.
5. Project eligible events with `scripts/project_training.py`. Keep every row marked `candidate` until a separate checker and the data owner approve it.
6. Attach a domain `I AM` surface: what the domain notices, refuses, and hands off. This is a bounded domain role, not a claim that the domain is a person.
7. Return source IDs, redaction status, checker evidence, assumptions, and one next seed. Stop at the configured cycle, turn, and child-depth caps.

## Trail-to-training rule

The trail is the archive. Training data is a derived view:

```text
checked frame -> redacted projection -> candidate row -> independent review -> approved dataset
```

Use the marketplace message convention in the candidate input:

```text
@<agent> /<plugin>:<skill> "<intent>" #trail:<trail_id>
```

Keep the JSON frame or evidence object as structured metadata. Do not train on the convention line alone, and do not rewrite the source trail to make a nicer example.

Fine-tuning quality is evidence-weighted, not transcript-volume-weighted: retain exact source event IDs, earned constraints, checker verdicts, corrections, failure modes, outcome tier, and redaction status. A longer trail is useful only when it improves provenance and reproducibility. A counterexample can teach a bounded pattern, but it cannot be promoted as execution truth.

## Eligibility and refusals

Only project events with an explicit successful status (`complete` or `pass`), a parent/source ID, and observable evidence. Exclude `open`, `loop`, `blocked`, unverified simulations, secrets, private tokens, raw credentials, and unapproved third-party personal data. A generated `I AM` passage may be retained as a labeled role-play example, but never as factual evidence about a philosopher or a conscious agent.

Refuse or escalate when the request asks to train directly on an entire transcript, identify a private person without authorization, use an unverified trail as truth, or generate a forward product that impersonates the end user.

## Domain surfaces

Each discovered domain must provide `id`, `entrypoints`, `iAm`, `scope`, `loadWhen`, `artifacts`, and `checker` fields. Start with `dotnet-skills` when the trail concerns skill structure; its recorded convention requires a skill folder, an agent under `agents/`, and progressive `scripts/`, `references/`, and `assets/` resources. Verify a live repository before treating a trail note as current.

## Flow-specific handoff

For backward flow, hand off an earned constraint, source event IDs, a proposed skill/template change, and a new checker seed. For forward flow, hand off declared user context, personalization decisions, quality evidence, assumptions, and the deliverable. “Best seller” is an evaluation target, never a guaranteed outcome.

## Resources

- Read `references/domain-registry.md` when a trail names a new domain or marketplace.
- Read `references/training-projection.md` before projecting any event into training data.
- Read `references/progressive-disclosure.md` when running with local or smaller models.
- Use `assets/domain-registry.json` as the bounded registry input.
- Run `scripts/project_training.py` for deterministic redacted JSONL projection.
