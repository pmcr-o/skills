# Progressive-trail examples

## Purpose

`domain-registry.json` documents the bounded domains and entrypoints that a
trail-to-skill or trail-to-product projection may discover.

## Inputs

The projection script consumes registry entries and checked, redacted trail
events with explicit flow direction.

## Expected output

The result is a candidate training/product projection with provenance,
redaction, domain identity, and checker requirements.

## Evidence and limits

Registry entries are discovery metadata. They do not prove a live repository,
provider, MCP server, MAF runtime, or model-training job exists.
