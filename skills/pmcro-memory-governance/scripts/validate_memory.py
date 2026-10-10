#!/usr/bin/env python3
"""Validate one PMCR-O memory record without changing it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED = {
    "apiVersion", "kind", "id", "version", "type", "scope", "owner", "content",
    "source", "evidence", "consent", "security", "freshness", "lifecycle", "retrieval",
}
SCOPES = {"global", "personal", "project", "run", "session"}
TYPES = {"instruction", "preference", "lesson", "earned-constraint", "session-state", "checkpoint", "raw-trail"}
TIERS = {"pattern-valid", "execution-verified", "production-verified", "unknown"}
SECRET_PATTERNS = (r"(?i)api[_-]?key\s*=", r"(?i)secret\s*[:=]", r"(?i)password\s*[:=]", r"-----BEGIN [A-Z ]+ KEY-----")


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    value = json.loads(args.record.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED - value.keys())
    if missing:
        fail(f"missing fields: {', '.join(missing)}")
    if value["apiVersion"] != "pmcro.dev/v1" or value["kind"] != "MemoryRecord":
        fail("invalid memory kind")
    if value["scope"] not in SCOPES or value["type"] not in TYPES:
        fail("invalid scope or type")
    if not value["id"] or not value["owner"] or not value["content"]:
        fail("id, owner, and content are required")
    source = value["source"]
    evidence = value["evidence"]
    consent = value["consent"]
    security = value["security"]
    freshness = value["freshness"]
    lifecycle = value["lifecycle"]
    retrieval = value["retrieval"]
    if not source.get("trailRef") or not source.get("frameRefs") or not source.get("checkerRef"):
        fail("provenance requires trailRef, frameRefs, and checkerRef")
    if evidence.get("tier") not in TIERS or evidence.get("verdict") not in {"PASS", "LOOP", "HALT", "UNKNOWN"}:
        fail("invalid evidence")
    if consent.get("redacted") is not True or not consent.get("purpose") or not consent.get("retention"):
        fail("consent must include purpose, redaction, and retention")
    if security.get("secretFree") is not True or not security.get("classification"):
        fail("security must declare secretFree and classification")
    for field in ("createdAt", "lastVerifiedAt", "refresh"):
        if not freshness.get(field):
            fail(f"freshness missing {field}")
    if lifecycle.get("status") not in {"candidate", "accepted", "deprecated", "revoked"}:
        fail("invalid lifecycle status")
    if lifecycle.get("status") == "accepted" and (
        evidence.get("verdict") != "PASS" or evidence.get("tier") not in {"execution-verified", "production-verified"}
    ):
        fail("accepted lessons require a checked execution or production tier")
    if not isinstance(retrieval.get("maxTokens"), int) or not 1 <= retrieval["maxTokens"] <= 2000:
        fail("retrieval maxTokens must be between 1 and 2000")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, value["content"]):
            fail("content resembles a secret")
    print(f"PASS: memory record {value['id']} is {lifecycle['status']} and {evidence['tier']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
