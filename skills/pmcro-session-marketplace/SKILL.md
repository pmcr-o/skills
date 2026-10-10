---
name: pmcro-session-marketplace
description: Convert an authorized long session export into a redacted PMCR-O trail, typed marketplace candidate, and labeled training inputs with bounded recursive next-seed routing. Use when a prior session must become a reusable product without treating transcript claims as runtime proof.
---

# PMCR-O session marketplace

This skill turns one user-authorized session file into a staged artifact graph:

```text
authorized source -> source manifest -> PMCR-O frames -> candidate skill
                                       -> candidate training rows
                                       -> independent check -> reflect seed
```

The raw source is preserved read-only only when the caller explicitly requests
a full-session package. The derived views are redacted and provenance-linked.

## Message contract

Every generated package declares four typed surfaces:

- `input`: source reference, owner/consent, domain hints, scope, and caps;
- `output`: paths, hashes, frame references, evidence tier, and simulation flags;
- `accept`: conditions that allow staging or a checked candidate;
- `deny`: conditions that block execution, promotion, training registration, or
  claims of live access.

The same shape is used for application adapters and training rows. A simulated
MCP call, terminal action, MAF workflow, provider capability, or code result is
valid as a labeled design candidate, but it must say `simulation: true` and
`verified: false`; it cannot become runtime evidence.

## Bounded loop

1. Register the uploaded source and hash it.
2. Derive the smallest PMCR-O graph and preserve claims as candidate/unknown.
3. Generate the staged marketplace and training projections.
4. Run `validate_package.py` as a separate independent checker process.
5. Invoke the marketplace `reflect` skill only after the checker frame is
   complete. The reflector emits one unexecuted messy seed.
6. Route that seed through a new `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`
   cycle only when a later bounded run explicitly admits it.

No step logs into a provider, opens W:, runs a remote command, trains a model,
publishes a marketplace, or promotes a candidate. Those are separate adapters
requiring their own charter and evidence.

## Manual run

```bash
python3 scripts/ingest_session.py \
  --source /path/to/authorized-session.txt \
  --out /path/to/staging \
  --include-raw \
  --max-cycles 3

python3 scripts/validate_package.py /path/to/staging
python3 ../reflect/scripts/reflect.py \
  --queue /path/to/staging/pmcro/frames.jsonl \
  --level meta2 \
  --prompt-intent "Re-open the staged session as raw intent and add one evidence-backed domain adapter." \
  --required-resource pmcro-session-marketplace \
  --append /path/to/staging/pmcro/frames.jsonl
python3 ../reflect/scripts/route_seed.py /path/to/staging/pmcro/frames.jsonl
```

The output is a staged candidate. A separate checker must validate any child
skill before promotion.
