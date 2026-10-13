# Memory-governance examples

## Purpose

The fixtures demonstrate a promotable memory record and a rejected secret-like
candidate.

## Inputs

`valid-memory-record.json` and `invalid-memory-record.json` are consumed by
`scripts/validate_memory.py`.

## Expected output

The valid record is accepted. The invalid record fails provenance/secret and
governance checks.

## Evidence and limits

The secret-like marker in the invalid fixture is synthetic test data, not a
credential. Validation proves the local schema and policy checks only; it does
not write to a memory provider or promote a lesson.
