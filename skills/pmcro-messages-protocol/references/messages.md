# PMCR-O role-owned message protocol

Each JSONL object is one append-only frame. A cycle is replayable from its frames without replaying the originating conversation.

## Envelope

Every frame contains:

| Field | Rule |
| --- | --- |
| `frame_id` | Unique frame identifier. |
| `trail_id`, `cycle_id` | Stable trail and cycle identifiers. |
| `seq` | Contiguous integer beginning at `1` within the cycle. |
| `role` | `orchestrator`, `planner`, `maker`, `checker`, or `reflector`. |
| `kind` | The role-owned kind listed below. |
| `parent_id` | The immediately preceding frame; `null` for the first frame. |
| `prev_hash` | Previous frame hash; `null` for the first frame. |
| `hash` | SHA-256 of the canonical frame with `hash` omitted. |
| `status` | `open`, `complete`, `blocked`, or `halted`. |
| `payload` | Only the fields owned by the role and kind. |

Canonical hashing uses UTF-8 JSON with `sort_keys=True`, separators `(',', ':')`, and `ensure_ascii=False`. Remove only the top-level `hash` field before hashing. The stored `hash` is the lowercase hexadecimal SHA-256 digest.

## Role-owned kinds

### `orchestrator.route`

Required payload fields: `goal`, `scope`, `next_role`, and `caps`. `caps` contains finite `loops`, `calls`, and `seconds`. The orchestrator establishes the charter and routes the next role; it never emits a plan or verdict.

### `planner.plan`

Required payload fields: `acceptance_criteria`, `validated_resources`, and ordered `steps`. Every resource must identify what was validated, such as a package ID, path, hash, commit, or evidence reference. The planner never executes commands or writes maker output.

### `maker.result`

Required payload fields: `plan_ref`, `files_changed`, `commands`, and `claim`. Each changed file has `path`, `action`, and `sha256`. Each command has an exit code and evidence reference. `claim` may be `complete`, `partial`, or `blocked`; the maker has no `verdict` field.

### `checker.verdict`

Required payload fields: `plan_ref`, `maker_ref`, `verdict`, `checks`, and `independent`. `verdict` is exactly `PASS`, `LOOP`, or `HALT`; `independent` must be `true`. Each check names its proof command, result, and evidence reference. The checker never edits maker output. A `LOOP` carries exactly one `repair_seed`; the orchestrator admits the bounded repair route. `HALT` ends the cycle.

### `reflector.reflect`

Required payload fields: `observations`, `earned_constraints`, and `next_seed`. An earned constraint is either `candidate` or `promoted` and carries `source_trail_refs` plus an `acceptance_basis` of `ACCEPT`. `next_seed` has:

```json
{
  "level": "meta|meta2|meta3",
  "prompt_intent": "one bounded unexecuted request",
  "required_resources": ["exact-package-or-frame-ref"],
  "unexecuted": true
}
```

`meta` repairs the current artifact or phase, `meta2` repairs a skill/workflow contract, and `meta3` repairs the orchestrator, agent surface, or prompt-routing system. The reflector records the seed; it does not run it.

## Admission and replay

The normal route is:

```text
orchestrator.route -> planner.plan -> maker.result -> checker.verdict -> reflector.reflect
```

The next frame is admitted only when the previous frame is `complete`. A `LOOP` is a bounded repair outcome, not a self-approved continuation. A new session receives references and asks for an exact missing package only when it cannot access that resource. Credentials, account recovery codes, and full transcripts are never default handoff material.
