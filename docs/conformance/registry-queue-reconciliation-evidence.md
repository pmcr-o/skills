# Registry and queue reconciliation evidence

Source Cycle base: `329fbf80897a41fcf567cd36a28421304d13f544`

Source marketplace: `A:\marketplace` (read-only)

## Source evidence inspected

- `pmcro-agent/.pmcro/control/capabilities.json`, `lifecycle.json`, `queue.json`, and `routing.json`
- `skill-creator-agent/.pmcro/control/capabilities.json` and `lifecycle.json`
- `skill-creator-agent/.pmcro/queue/config.json` and queue message schema
- `eng/install-message-queue.py`
- `eng/src/foundation-protocol/messages.md` and `skill-create-message.schema.json`
- `eng/src/resource-registry/lib/registry_core.py`
- Skill Creator CREATE/READ/UPDATE/DELETE skill contracts

## Adopted or merged

- durable immutable message envelope with trace/correlation/causation, trail/cycle references, evidence status, grants, and content/dedupe digests
- at-least-once filesystem-spool semantics with atomic moves, bounded lease/retry/dead-letter behavior, separated mutable delivery state, and immutable ACK receipts
- local trail ownership across agents instead of a shared mutable trail
- content-addressed checked registry records, append-only revocation, and registry-backed Planner resolution
- explicit separation of Skill Creator CREATE from READ, UPDATE, DELETE, REGISTER, and later USE

## Explicitly rejected or narrowed

- queue delivery grants no authority and cannot inject a cognitive phase
- `reflector.reflect` does not autonomously execute its emitted seed
- the A-drive Skill Creator requirement for all optional folders/files was superseded by progressive disclosure: `SKILL.md + agents/` is the required core
- filesystem-spool-v1 remains `candidate-unregistered` in the C: canonical registry until a later independent transport-registration Cycle

## Deterministic validation

- focused registry/queue reconciliation tests: 9 PASS
- repository suite: 77 PASS
- Skill Creator tests: 5 PASS
- capability route tests: 3 PASS
- capability import tests: 3 PASS
- repository structural validator: PASS (`148 required files, 12 agent surfaces, 222 trail events`)
- JSON parse: 111 files PASS
- `git diff --check`: PASS
- A-drive marketplace Git status before/after: 308 entries each, semantic diff count 0

No A-drive file, queue, trail, registry, or generated project was modified. No transport was registered for execution. No model was trained, pulled, bound, or activated.
