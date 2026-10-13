#!/usr/bin/env python3
"""Validate the provider-neutral PMCR-O product repository template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = (
    "README.md",
    "product.manifest.json",
    "autonomy-grant.example.json",
    ".agents/README.md",
    ".agents/agents/orchestrator.json",
    ".agents/agents/checker.json",
    ".agents/agents/reflector.json",
    ".pmcro/protocol/trail-event.schema.json",
    ".pmcro/trails/example.jsonl",
    ".pmcro/trails/README.md",
    "scripts/validate.ps1",
    "scripts/validate_trail.py",
    "tests/README.md",
)
PHASES = {"orchestrate", "plan", "make", "check", "reflect"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON: {path}: {exc}") from exc


def validate(root: Path) -> None:
    for relative in REQUIRED:
        if not (root / relative).is_file():
            raise AssertionError(f"missing product-repo file: {relative}")

    manifest = load(root / "product.manifest.json")
    if manifest.get("apiVersion") != "pmcro.product-repo/v1":
        raise AssertionError("product manifest apiVersion is invalid")
    if manifest.get("trailContract") != ".pmcro/protocol/trail-event.schema.json":
        raise AssertionError("product manifest must point to the generic trail contract")
    if manifest.get("promotion") != "checker-verified-only":
        raise AssertionError("product promotion must require a checker")
    limits = manifest.get("limits", {})
    for key in ("iterations", "toolCalls", "deadlineMs", "maxDepth"):
        if not isinstance(limits.get(key), int) or limits[key] <= 0:
            raise AssertionError(f"product limit must be a positive integer: {key}")

    grant = load(root / "autonomy-grant.example.json")
    if grant.get("checker", {}).get("required") is not True:
        raise AssertionError("autonomy grant must require a separate checker")
    if grant.get("autoApprove") is not True:
        raise AssertionError("example grant must demonstrate bounded autoApprove")
    if "credentials" in grant.get("scope", {}).get("operations", []):
        raise AssertionError("credentials cannot be an autonomy operation")
    grant_limits = grant.get("limits", {})
    if not all(isinstance(grant_limits.get(key), int) and grant_limits[key] > 0 for key in ("iterations", "toolCalls", "deadlineMs", "maxDepth")):
        raise AssertionError("autonomy grant limits are incomplete")

    agents = {path.stem: load(path) for path in (root / ".agents/agents").glob("*.json")}
    if set(agents) != {"orchestrator", "checker", "reflector"}:
        raise AssertionError("product template must expose orchestrator, checker, and reflector")
    if agents["checker"].get("independentChecker") is not True:
        raise AssertionError("product checker must be independent")
    if agents["checker"].get("maxTurns") != 1:
        raise AssertionError("product checker must have a one-turn cap")
    if agents["orchestrator"].get("canDelegate") is not True:
        raise AssertionError("product orchestrator must be able to delegate inside its grant")

    schema = load(root / ".pmcro/protocol/trail-event.schema.json")
    required = set(schema.get("required", []))
    if not {"trailId", "cycleId", "eventId", "phase", "role", "iAm", "act", "status", "evidenceRefs"}.issubset(required):
        raise AssertionError("generic trail schema is missing its identity/evidence fields")

    events = [json.loads(line) for line in (root / ".pmcro/trails/example.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not events or {event.get("phase") for event in events} != PHASES:
        raise AssertionError("example trail must cover every PMCR-O phase")
    seen = set()
    for event in events:
        for field in ("trailId", "cycleId", "eventId", "phase", "role", "iAm", "act", "status", "evidenceRefs"):
            if field not in event:
                raise AssertionError(f"trail event missing {field}")
        if event["phase"] not in PHASES:
            raise AssertionError(f"unknown trail phase: {event['phase']}")
        parent = event.get("parentId")
        if parent is not None and parent not in seen:
            raise AssertionError(f"trail parent is not append-only: {event['eventId']}")
        seen.add(event["eventId"])
    if not any(event["role"] == "checker" and event["status"] == "verified" for event in events):
        raise AssertionError("example trail must contain a verified checker event")
    print(f"PASS: product repository template; events={len(events)}; agents={len(agents)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3] / "templates/product-repo")
    args = parser.parse_args()
    validate(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
