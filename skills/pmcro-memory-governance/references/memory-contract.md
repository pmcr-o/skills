# Memory record contract

Active memory is a small, typed projection of evidence. It is not a dump of a
conversation and it is not a model-weight update.

Required fields:

```json
{
  "apiVersion": "pmcro.dev/v1",
  "kind": "MemoryRecord",
  "id": "memory.example.constraint",
  "version": "1.0.0",
  "type": "earned-constraint",
  "scope": "project",
  "owner": "project:example",
  "content": "...",
  "source": {"trailRef": "...", "frameRefs": [], "checkerRef": "..."},
  "evidence": {"tier": "execution-verified", "verdict": "PASS"},
  "consent": {"purpose": "project-agent-quality", "redacted": true, "retention": "until-revoked"},
  "security": {"classification": "internal", "secretFree": true, "encryptionRequired": true},
  "freshness": {"createdAt": "...", "lastVerifiedAt": "...", "expiresAt": null, "refresh": "on-source-change"},
  "lifecycle": {"status": "accepted", "supersedes": [], "revokedAt": null},
  "retrieval": {"tags": [], "maxTokens": 300}
}
```

Scope must be one of `global`, `personal`, `project`, `run`, or `session`.
Global records require policy ownership. Personal records do not become global
by being retrieved by another agent. `run` and `session` records expire unless
explicitly promoted.

`candidate` is the safe default. An `accepted` lesson or earned constraint
requires `evidence.verdict=PASS`, a checker ref, redaction, and a non-unknown
evidence tier. `deprecated` and `revoked` records remain auditable but are not
retrievable as active guidance.
