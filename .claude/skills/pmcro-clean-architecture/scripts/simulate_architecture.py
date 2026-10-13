#!/usr/bin/env python3
"""Emit a deterministic, simulation-only Clean Architecture build plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.]*$")
ENTITY_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    required = ("apiVersion", "kind", "requestId", "traceId", "applicationName", "rootNamespace", "targetFramework", "entities", "source", "target", "mode", "grant", "outputProfile")
    for field in required:
        if field not in request:
            fail(f"missing request field {field}")
    if request["apiVersion"] != "pmcro.dev/v1" or request["kind"] != "CleanArchitectureRequest":
        fail("invalid Clean Architecture request kind")
    if not NAME_RE.fullmatch(request["rootNamespace"]):
        fail("rootNamespace must be a dotted .NET identifier")
    if not re.fullmatch(r"^net[0-9]+\.[0-9]+$", request["targetFramework"]):
        fail("targetFramework must look like net8.0")
    if not request["entities"] or any(not ENTITY_RE.fullmatch(entity) for entity in request["entities"]):
        fail("entities must be PascalCase identifiers")
    if request["mode"] not in {"inspect", "simulate", "stage", "execute", "check"}:
        fail("unsupported mode")
    source = request["source"]
    source_type = source.get("type")
    if source_type == "repository":
        ref = source.get("ref") or {}
        if not ref.get("url") or not ref.get("commit") or not ref.get("license"):
            fail("repository source requires url, immutable commit, and license")
        source_summary = f"pinned:{ref['url']}@{ref['commit']}"
    elif source_type == "local-template":
        source_summary = "local-template"
    else:
        fail("source.type must be local-template or repository")

    root = request["rootNamespace"]
    entities = request["entities"]
    artifacts = [f"src/{root}.Domain/Entities/{entity}.cs" for entity in entities]
    artifacts.extend([
        f"src/{root}.Domain/EntityBase.cs",
        f"src/{root}.Application/Abstractions/IGenericRepository.cs",
        f"src/{root}.Application/Abstractions/IUnitOfWork.cs",
        f"src/{root}.Infrastructure/Persistence/GenericRepository.cs",
        f"src/{root}.Infrastructure/Persistence/UnitOfWork.cs",
        f"src/{root}.Api/AgentSurface.cs",
        f"tests/{root}.ArchitectureTests/ArchitectureContractTests.cs",
    ])
    result = {
        "apiVersion": "pmcro.dev/v1",
        "kind": "SkillOutput",
        "messageId": f"msg-{request['requestId']}",
        "traceId": request["traceId"],
        "parentMessageId": None,
        "from": {"skillId": "pmcro-clean-architecture", "surfaceId": "pmcro.clean-architecture"},
        "to": {"skillId": "checker", "role": "independent-checker"},
        "phase": "make",
        "mode": request["mode"],
        "status": "complete",
        "simulation": True,
        "verified": False,
        "evidenceTier": "pattern-valid",
        "input": {"refs": [f"application:{request['applicationName']}", f"framework:{request['targetFramework']}", f"source:{source_summary}"], "summary": f"Build Clean Architecture plan for {request['applicationName']}"},
        "output": {"summary": "staged Clean Architecture layer plan", "artifacts": artifacts, "decisions": ["EntityBase<Guid>", "IGenericRepository<TEntity>", "IUnitOfWork", "agent-surface-staged", "runtime-map:maf-workflows-codeact-harness-mcp"]},
        "accept": ["application identity and target scope explicit", "generic repository constraint declared", "source provenance explicit", "checker validates generated layout"],
        "deny": ["unknown overwrite", "un pinned repository", "silent package install", "simulation as execution", "self-approval"],
        "evidence": ["simulation:clean-architecture-layer-plan", "source:" + source_summary, "grant:" + request["grant"]["sideEffects"]],
        "next": {"action": "handoff", "to": "independent-checker", "unexecuted": True, "seedLevel": "meta2"},
        "architecture": {"layers": ["Domain", "Application", "Infrastructure", "API/worker", "Tests"], "entities": entities, "repositoryConstraint": "where TEntity : EntityBase", "unitOfWork": "Repository<TEntity>()", "targetRoot": request["target"]["root"]},
        "runtime": {"mafWorkflow": "role-graph-checkpoints-resume", "codeAct": "bounded-maker-or-worker-executor", "harness": "host-policy-sandbox-budget-evidence", "mcp": "typed-allowlisted-capability-boundary", "checker": "fresh-context-independent-verdict"},
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
