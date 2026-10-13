# PMCR-O Training Data Specification 1.0

Status: candidate specification

Normative terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are interpreted as requirement levels for PMCR-O conformance.

## 1. Scope

This specification defines how operational material becomes an eligible candidate for role-specific model training. It does not grant authority to train, pull, activate, or deploy any model.

## 2. Default state

All operational records MUST begin training-ineligible. Trail, Cycle, Frame, Evidence, chat, provider context, connected-source content, and runtime output MUST NOT become training data solely because PMCR-O observed or stored them.

## 3. Eligibility gate

A candidate training record MUST include:

1. `defaultEligible=false`;
2. explicit opt-in;
3. at least one immutable provenance reference;
4. completed sanitization with a redaction-report reference;
5. an exclusion-class declaration covering at minimum secrets, credentials, private reasoning, and unapproved user content;
6. an independent checker verdict reference;
7. a target PMCR-O role profile;
8. a dataset split that prevents evaluation leakage.

The machine-readable base eligibility contract is `.pmcro/protocol/training-data-eligibility.schema.json`.

## 4. Lifecycle

`OBSERVED -> CANDIDATE -> ELIGIBILITY GATE -> SANITIZE -> CHECK -> DATASET CANDIDATE -> DATASET VERSION -> ROLE EVAL -> TRAINING-READY`

`TRAINING-READY` MUST NOT be interpreted as permission to invoke training. Training execution requires a separately admitted capability and grant.

## 5. Role separation

PMCR-O maintains separately addressable profiles for `pmcro-orchestrator`, `pmcro-planner`, `pmcro-maker`, `pmcro-checker`, and `pmcro-reflector`.

Maker and Checker datasets MUST be independently versioned. Checker evaluation SHOULD emphasize adversarial defect detection, evidence sufficiency, verdict classification, and no-repair behavior. Maker evaluation SHOULD emphasize plan fidelity, admitted capability use, evidence completeness, and stop-on-gap behavior.

A record MAY be eligible for more than one role only when the multi-role routing is explicit and independently checked.

## 6. Provenance

Dataset manifests MUST record source references, sanitization evidence, checker verdicts, policy version, role profile, dataset version, split assignment, and content hash or immutable equivalent.

Derived or synthetic records MUST record their generator and source lineage. Synthetic generation does not remove the eligibility gate.

## 7. Evaluation separation

Training and evaluation partitions MUST be distinct. Role-specific eval cases SHOULD remain outside training corpora. Evaluation result references belong to model lifecycle evidence and MUST NOT be fabricated from training metrics alone.

## 8. Exclusions

The following classes MUST NOT be admitted: secret values, credentials, private reasoning, unapproved user content, content lacking provenance, records without completed sanitization, and records without an independent checker verdict.

## 9. Registration

A dataset version MAY be registered only after deterministic schema validation and independent CHECK. A model binding MAY reference only a registered dataset version or an explicitly external checked dataset reference.
