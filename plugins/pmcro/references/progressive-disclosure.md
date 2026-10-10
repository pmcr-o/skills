# Progressive catalog disclosure

Keep the first handoff small enough for a local model or a second session:

1. **Metadata:** id, trigger, version, scope, source/ref, trust, and a short
   description.
2. **Contract:** `SKILL.md`, agent surface, input/output/accept/deny, grant,
   dependencies, and checker requirements.
3. **Implementation:** references, scripts, assets, tests, repository evidence,
   and the authorized raw trail only when the audience needs it.

The catalog returns references and hashes rather than copying a whole session.
Request a later packet by exact id. A full transcript is an authorized source
artifact, not the default activation context. This protects token budget and
reduces the chance that transient paths, secrets, or failed attempts become
accidental instructions.
