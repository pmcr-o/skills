# Message-protocol examples

## Purpose

The nested JSONL fixtures show valid and invalid role-owned protocol frames.

## Inputs

`examples/valid.jsonl` and `examples/invalid.jsonl` are consumed by the frame
validator and differ in their envelope/hash-chain validity.

## Expected output

The valid stream passes; the invalid stream fails with a bounded validation
error rather than being repaired silently.

## Evidence and limits

Validation proves the local message contract only. It does not execute a role,
approve maker work, or establish independent checker identity.
