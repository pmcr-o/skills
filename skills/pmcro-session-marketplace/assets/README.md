# Session-marketplace examples

## Purpose

These fixtures document the manifest and message contract for converting an
authorized session into a staged marketplace candidate.

## Inputs

`manifest.schema.json` defines the package fields. The nested
`examples/message-contract.json` shows typed input/output/accept/deny data.

## Expected output

The ingest scripts produce redacted source metadata, PMCR-O frames, candidate
training rows, checker evidence, and an unexecuted next seed.

## Evidence and limits

Examples are candidate projections, not automatic training or promotion. They
must not contain provider-private history, credentials, or unredacted personal
data.
