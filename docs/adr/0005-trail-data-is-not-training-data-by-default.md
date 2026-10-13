# ADR-0005: Trail data is not training data by default

Status: accepted

## Context

PMCR-O Trails contain operational history, evidence, requests, failures, context references, and provider/runtime observations. Automatic reuse of Trail content for model training would collapse operational logging, user content, secrets, and model-learning policy into one uncontrolled channel.

## Decision

Trail, Cycle, Frame, Evidence, chat, provider context, connected-source content, and runtime artifacts are training-ineligible by default.

A record may enter a training dataset only after explicit opt-in, immutable provenance, sanitization/redaction, exclusion-class checks, an independent checker verdict, and role-specific dataset routing.

Secrets, credentials, private reasoning, and unapproved user content MUST NOT enter training datasets. Training eligibility does not authorize model training; training itself is a separately admitted capability and lifecycle transition.

Maker and Checker training/evaluation corpora MUST remain separately addressable and MUST NOT use a Maker model's self-verdict as authoritative Checker evidence.

## Consequences

- Data collection and model training become separate governed lifecycle stages.
- Existing Trail retention does not imply dataset permission.
- Candidate datasets remain untrusted until independently checked.
- Every accepted dataset record can be traced to provenance, sanitization evidence, eligibility policy, and checker verdict.
