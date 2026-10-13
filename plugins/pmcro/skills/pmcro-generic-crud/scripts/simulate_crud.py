#!/usr/bin/env python3
"""Simulate bounded CRUD over a declarative PMCR-O resource."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OPERATIONS = {"create", "read", "update", "delete"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    for field in ("requestId", "traceId", "resource", "operation", "mode", "projection", "grant", "outputProfile"):
        if field not in request:
            raise SystemExit(f"FAIL: missing request field {field}")
    if request["kind"] != "CrudRequest" or request["apiVersion"] != "pmcro.dev/v1":
        raise SystemExit("FAIL: invalid CRUD request kind")
    operation = request["operation"]
    resource = request["resource"]
    if operation not in OPERATIONS:
        raise SystemExit(f"FAIL: unsupported operation {operation}")
    if request["mode"] not in {"inspect", "simulate", "execute", "check"}:
        raise SystemExit("FAIL: unsupported mode")

    outcome = {
        "create": ("staged", "new candidate version", "stage", "checker validates schema and parent"),
        "read": ("disclosed", "bounded projection", "read", "checker validates scope and disclosure"),
        "update": ("versioned", "successor linked to predecessor", "write", "checker validates expectedVersion and diff"),
        "delete": ("revocation-planned", "reversible tombstone", "revoke", "checker validates retention and reason"),
    }[operation]
    simulation = request["mode"] != "check"
    verified = False
    if request["mode"] == "execute":
        outcome = ("blocked", "local adapter does not execute mutations", "none", "real adapter and grant required")
    payload = request.get("payload", {})
    artifacts = [f"operation:{operation}", f"resourceVersion:{resource.get('version') or 'candidate'}"]
    architecture = payload.get("architecture")
    if architecture == "clean-architecture":
        artifacts.extend([
            "domain:EntityBase<Guid>",
            "application:IGenericRepository<TEntity>",
            "infrastructure:generic-implementation",
        ])
    if payload.get("unitOfWork"):
        artifacts.extend([
            "application:IUnitOfWork",
            "composition:Repository<TEntity>",
            "crud-for-new-entity:inherited-from-EntityBase",
        ])
    result = {
        "apiVersion": "pmcro.dev/v1",
        "kind": "SkillOutput",
        "messageId": f"msg-{request['requestId']}",
        "traceId": request["traceId"],
        "parentMessageId": None,
        "from": {"skillId": "pmcro-generic-crud", "surfaceId": "pmcro.generic-crud"},
        "to": {"skillId": "checker", "role": "independent-checker"},
        "phase": "make",
        "mode": request["mode"],
        "status": "complete" if outcome[0] != "blocked" else "blocked",
        "simulation": simulation,
        "verified": verified,
        "evidenceTier": "pattern-valid" if simulation else "unknown",
        "input": {"refs": [f"resource:{resource['kind']}/{resource['id']}", f"scope:{resource['scope']}"], "summary": f"{operation.upper()} {resource['kind']} {resource['id']}"},
        "output": {"summary": outcome[1], "artifacts": artifacts, "decisions": [outcome[0]]},
        "accept": ["operation explicit", "scope checked", outcome[3]],
        "deny": ["implicit overwrite", "physical delete by default", "scope widening", "simulation as execution"],
        "evidence": [f"simulation:crud:{operation}", f"grant:{outcome[2]}"],
        "next": {"action": "handoff", "unexecuted": True, "seedLevel": None},
        "crud": {"operation": operation, "resource": resource, "retention": payload.get("retention", "policy-required"), "architecture": architecture or "pmcro-resource"},
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
