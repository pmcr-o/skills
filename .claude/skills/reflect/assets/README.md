# Reflector examples

## Purpose

The nested checker queue fixture demonstrates that reflection waits for a
completed independent checker before emitting a next seed.

## Inputs

`examples/checker-queue.jsonl` is consumed by the reflector scripts with a
requested seed level and prompt intent.

## Expected output

The result contains an earned constraint and one `unexecuted=true` next seed.

## Evidence and limits

The fixture is a routing example. It does not execute the seed, certify the
maker, or prove a runtime correction.
