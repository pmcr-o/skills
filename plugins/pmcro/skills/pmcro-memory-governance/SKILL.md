---
name: pmcro-memory-governance
description: Govern production agent memory as typed, scoped, provenance-linked records with redaction, freshness, retention, revocation, evaluation, and independent promotion. Use when turning PMCR-O trails, MAF sessions, checkpoints, project instructions, or user preferences into reusable memory; never treat a prompt file as an enforcement boundary.
---

# PMCR-O memory governance

Use this skill to decide what may become durable memory and where it belongs.
Do not make one growing transcript or prompt file carry every kind of state.

## Memory classes

- `instruction`: human or policy-authored rules; versioned and reviewable.
- `preference`: principal-scoped choices; never silently shared.
- `lesson` / `earned-constraint`: checked, provenance-linked reusable behavior.
- `session-state`: ephemeral conversation/workflow state; access-controlled.
- `checkpoint`: resumable MAF workflow state; treat as sensitive.
- `raw-trail`: append-only source evidence; read-only and not default context.

## Procedure

1. Set `scope`, owner, purpose, classification, retention, and allowed readers.
2. Redact credentials, private reasoning, unrelated personal data, and secrets.
3. Link the record to exact trail/frame/checker refs and an evidence tier.
4. Store candidates separately. Promote only after an independent checker and
   policy decision; a model's narration cannot promote its own memory.
5. Add freshness, expiry/revocation, supersession, and a retrieval token budget.
6. Retrieve the smallest relevant projection. Return the record's provenance,
   status, and confidence with the content.
7. Revalidate after policy, source, schema, provider, or project changes.

Validate a record directly:

```bash
python3 scripts/validate_memory.py assets/valid-memory-record.json
python3 scripts/validate_memory.py assets/invalid-memory-record.json  # expected exit 1
```

MAF workflow state and checkpoints are runtime state, not automatically
marketplace knowledge. Provider files such as `CLAUDE.md` or `AGENTS.md` are
portable projections and context inputs; hard enforcement belongs in grants,
settings, hooks, tool policies, and the independent checker.

Read `references/memory-contract.md` for the schema and
`references/enterprise-checklist.md` for the release gate.
