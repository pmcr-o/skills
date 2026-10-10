#!/usr/bin/env python3
"""Read-only simulation of the PMCR-O agent-surface API."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote


ROUTE_PATTERNS = (
    ("global", re.compile(r"^/v1/scopes/global/agents/([^/]+)$")),
    ("personal", re.compile(r"^/v1/users/([^/]+)/agents/([^/]+)$")),
    ("project", re.compile(r"^/v1/projects/([^/]+)/agents/([^/]+)$")),
)


def load_surfaces(repo: Path) -> dict[str, dict]:
    surfaces: dict[str, dict] = {}
    for path in sorted((repo / ".agents" / "agents").glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if value.get("kind") == "AgentSurface":
            surfaces[value["id"]] = value
    return surfaces


def response(status_code: int, request: dict, status: dict, **extra) -> dict:
    result = {
        "apiVersion": "pmcro.dev/v1",
        "kind": "AgentSurfaceResponse",
        "statusCode": status_code,
        "request": request,
        "status": status,
    }
    result.update(extra)
    return result


def simulated_status(mode: str, trace_id: str) -> dict:
    return {
        "mode": mode,
        "simulation": True,
        "verified": False,
        "evidenceTier": "pattern-valid",
        "traceId": trace_id,
        "checkerRef": None,
        "trailRef": "trail:agent-surface-simulation",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    method = str(request.get("method", "GET")).upper()
    path = str(request.get("path", ""))
    mode = str(request.get("mode", "inspect"))
    trace_id = str(request.get("traceId", "trace-surface-unknown"))
    surfaces = load_surfaces(args.repo)
    status = simulated_status(mode, trace_id)

    if method == "POST" and path == "/v1/orchestrator-runs":
        candidates = request.get("candidateAgents", [])
        return print(json.dumps(response(
            202,
            request,
            status,
            run={
                "runId": "run-surface-simulation-001",
                "candidates": candidates,
                "predictedTransitions": ["orchestrate", "plan", "make", "check", "reflect"],
                "requiredEvidence": ["independent checker verdict", "trail frame", "acceptance output"],
            },
        ), ensure_ascii=False)) or 0

    if method != "GET":
        print(json.dumps(response(405, request, status, error="only GET surface inspection is simulated")))
        return 0

    for expected_scope, pattern in ROUTE_PATTERNS:
        match = pattern.match(path)
        if not match:
            continue
        groups = [unquote(group) for group in match.groups()]
        agent_id = groups[-1]
        surface = surfaces.get(agent_id)
        if surface is None:
            print(json.dumps(response(404, request, status, error="agent surface not found", agentId=agent_id)))
            return 0
        if surface.get("scope") != expected_scope:
            print(json.dumps(response(403, request, status, error="scope mismatch", agentId=agent_id)))
            return 0
        print(json.dumps(response(
            200,
            request,
            status,
            agent=surface,
            predictedTransitions=["resolve", "authorize", "inspect", "handoff"],
            requiredEvidence=["scope resolution", "dependency refs", "independent checker"],
        ), ensure_ascii=False))
        return 0

    print(json.dumps(response(404, request, status, error="route not modeled by this local simulation")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
