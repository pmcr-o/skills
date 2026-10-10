#!/usr/bin/env python3
"""Validate the small repository-local agent-surface projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = {
    "apiVersion", "kind", "id", "version", "scope", "owner", "templateRef",
    "entrypoints", "inputs", "outputs", "accept", "deny", "dependencies",
    "modes", "grant", "limits", "status",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.repo / ".agents" / "agents"
    paths = [root / name for name in ("global-orchestrator.json", "personal-orchestrator.json", "projectname-orchestration-service.json")]
    surfaces = []
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        missing = sorted(REQUIRED - value.keys())
        if missing:
            raise SystemExit(f"FAIL: {path}: missing {', '.join(missing)}")
        if value["apiVersion"] != "pmcro.dev/v1" or value["kind"] != "AgentSurface":
            raise SystemExit(f"FAIL: {path}: invalid kind")
        if value["status"]["simulation"] is not True or value["status"]["verified"] is not False:
            raise SystemExit(f"FAIL: {path}: initial surface must be simulation-only")
        surfaces.append(value)
    by_id = {value["id"]: value for value in surfaces}
    personal = by_id["pmcro.personal-orchestrator"]
    if personal["extends"]["ref"] != "pmcro.global-orchestrator" or personal["extends"]["policy"] != "non-widening":
        raise SystemExit("FAIL: personal surface must inherit the global surface non-wideningly")
    project = by_id["projectname.orchestration-service"]
    if project["capabilityType"] != "service" or project["scope"] != "project":
        raise SystemExit("FAIL: project service surface must remain a project-scoped service")
    print(f"PASS: {len(surfaces)} agent surfaces validated; simulation-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
