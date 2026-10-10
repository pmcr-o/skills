# Training-data projection

Training data is a derived product of a checked trail, not a second name for the trail.

## Candidate row

Use a row shaped like:

```json
{
  "status": "candidate",
  "flow": "backward",
  "messages": [
    {"role": "user", "content": "@reflector /pmcro:reflect \"...\" #trail:T-001"},
    {"role": "assistant", "content": "{...checked handoff...}"}
  ],
  "metadata": {
    "trail_id": "T-001",
    "source_event_ids": ["check-001"],
    "domain": "pmcro",
    "principal_ref": "principal:masked",
    "redaction": "applied"
  }
}
```

## Backward projection

Use checked evidence to propose one reusable constraint or skill change. Preserve the source event IDs and mark the target as a candidate. Do not train a model to repeat an accidental behavior merely because it appeared often.

## Forward projection

Use a checked trail product plus declared user identity and intent to generate a deliverable. Keep identity scoped to the product request; do not copy private memories into a reusable training template. Record quality evidence and uncertainty. Commercial language such as “best seller” remains a goal for evaluation, not a factual label.

## Redaction and provenance

Mask secrets and direct identifiers before projection. Keep stable references to the source event, trail, Git checkpoint, and checker verdict so an approved dataset can be audited back to its origin. A redacted row must not be treated as approved merely because it is syntactically valid.

## Simulation boundary

If the source contains a simulated philosopher voice or a simulated tool result, label it as simulation in metadata. It may teach the format of a role-play frame; it may not teach the model that the historical thinker or external action actually occurred.
