---
name: pmcro-product-repo
description: Generate a provider-neutral product repository that lets a Codex, Claude, or local agent run a bounded near-autonomous PMCR-O loop with revocable grants, generic trails, independent checks, and friend-ready activation instructions.
---

# PMCR-O product repository

Use this skill when a user wants an agent-ready product repository rather
than a one-off prompt or transcript.

1. Emit `skill.create.request` through `@skill-creator /create-skill`.
2. Load `templates/product-repo/` and derive the smallest product manifest.
3. Issue or validate a finite autonomy grant. `autoApprove` may continue
   routine work only inside that grant; it never permits scope expansion.
4. Create only the declared repository paths, provider adapters, and tests.
5. Append generic PMCR-O trail events for intent, roles, artifacts, evidence,
   corrections, and the unexecuted next seed.
6. Send the result to a separate checker, then reflect and stage the product.
7. Package the checked repository as progressive text activation for a friend.

The generic trail carries identity, scope, act, artifact references, evidence,
simulation state, and checker status. Domain details belong in artifacts or
references, not in a second trail format.

Routine local reads, builds, tests, and bounded writes may continue under an
active grant. Stop or escalate for credentials, external writes, deletion,
publishing, scope changes, expired grants, or repeated failure.
