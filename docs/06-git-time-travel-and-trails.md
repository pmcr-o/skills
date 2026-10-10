# Cognitive trails and Git “time travel”

A trail is a sequence of provenance-linked events. A Git repository gives the artifact side of that history; the PMCR-O trail gives the intent, role, context, decision, and evidence side.

## Event shape

The small schema in `.pmcro/protocol/trail-schema.json` is intentionally permissive, but each event should normally include:

- `eventId` and `parentId`;
- phase and role;
- principal and `contextId`;
- charter and capability scope;
- action and output;
- evidence and status; and
- a Git reference when an artifact checkpoint exists.

## Replay versus rewrite

“Time travel” means:

- inspect an earlier Git commit;
- reconstruct the trail up to a selected event;
- branch from that checkpoint for a new experiment; or
- compare two handoffs.

It does not mean changing a past verdict, pretending an unexecuted action happened, or inheriting credentials from an old context. A replay is read-only until a new, explicitly chartered branch is opened.

## Trail cascade

The trail can cascade across domains without losing provenance:

```text
cognitive trail
  -> intent envelope
  -> PMCR-O phase trail
  -> domain child trail (MAF, Figma, Docker, Git, marketplace)
  -> checked handoff
  -> next seed
```

Each child trail should link back to its parent event and preserve its own limits. A Figma event should not inherit Docker authority merely because both descend from the same company cycle.

## Backward/forward trail semantics

The same trail can be read in two directions:

- **Backward:** start with checked outcomes, identify an earned constraint, and update a reusable skill or template. This is learning from experience; it must preserve source provenance and remain subject to a new checker.
- **Forward:** start with a checked trail product, attach a user’s declared identity and intent, and generate a deliverable. This is product use; it must record the user context, personalization decisions, quality evidence, and any uncertainty.

MCP can carry the handoff between these nodes, but it should not collapse the provenance boundary. A tool response is evidence attached to a trail event, not a replacement for the trail.

## Git as a story of work

Git history is valuable because it records artifact transitions: draft, checked, staged, promoted, or reverted. The PMCR-O trail complements it by recording why the transition was attempted and who or what checked it. Neither layer alone is the whole story.
